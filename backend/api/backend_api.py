from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.domain_gen import get_amazon_domain
from services.amazon_scraper import amazon_category_top_products, scrape_amazon_product
from services.prompt_builder import build_and_get_categories
from services.sorting_algorithm import SortingAlgorithm
import re
from threading import Lock
from queue import Queue
import random

app = Flask(__name__)
app.config['APP_NAME'] = 'Eventually Yours Shopping App'

# Configure CORS with more permissive settings
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Session-Id", "X-Requested-With"],
        "expose_headers": ["Content-Type", "X-Session-Id"],
        "supports_credentials": True
    }
})

# Load environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Global variables to store user data and results
user_sessions = {}

# Global variables for concurrent processing
request_queue = Queue()
processing_lock = Lock()
active_requests = {}
request_results = {}

# Worker pool for concurrent processing - reduced for deployment
worker_pool = ThreadPoolExecutor(max_workers=2)  # Reduced from 3 to 2


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Eventually Yours Shopping App Backend API is running",
        "app_name": app.config['APP_NAME']
    })


@app.route("/api/init-session", methods=["POST", "OPTIONS"])
def init_session():
    """Initialize a new session when user lands on the page"""
    if request.method == "OPTIONS":
        # Handle preflight request
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Session-Id")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response
        
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        print(f"Initializing session: {session_id}")
        
        if not session_id:
            return jsonify({"status": "error", "message": "Session ID is required"}), 400
        
        # Initialize session with empty user data
        user_sessions[session_id] = {"user_data": {}}
        
        print(f"Session initialized: {session_id}")
        print(f"Total sessions now: {len(user_sessions)}")
        print(f"Session keys: {list(user_sessions.keys())}")
        
        return jsonify({
            "status": "success",
            "message": "Session initialized successfully",
            "session_id": session_id
        })
    except Exception as e:
        print(f"Error initializing session: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/user-info", methods=["POST", "OPTIONS"])
def store_user_info():
    """Store user information from the frontend"""
    if request.method == "OPTIONS":
        # Handle preflight request
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Session-Id")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response
        
    try:
        # Debug: Log request details
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request content type: {request.content_type}")
        print(f"Request content length: {request.content_length}")
        
        # Check if request has JSON content
        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({
                "status": "error", 
                "message": "Content-Type must be application/json",
                "received_content_type": request.content_type
            }), 415
        
        data = request.get_json()
        if data is None:
            print("Error: Failed to parse JSON data")
            return jsonify({
                "status": "error", 
                "message": "Invalid JSON data"
            }), 400
            
        print(f"Received user info data: {data}")
        
        # Check for session ID in headers first, then in data
        session_id = request.headers.get("X-Session-Id") or data.get("session_id")
        print(f"Session ID from request: {session_id}")

        # Extract and format user data
        try:
            # Ensure categories is always a list
            categories = data.get("categories", [])
            if isinstance(categories, str):
                categories = [categories]
            elif not isinstance(categories, list):
                categories = []
            
            user_data = {
                "age": data.get("age", ""),
                "gender": data.get("gender", ""),
                "favorite_categories": categories,
                "interests": data.get("interests", ""),
                "preferred_shopping_method": "online",  # Default since it's a web app
                "user_location": data.get("location", ""),
                "budget_range": (
                    f"{data.get('budgetMin', '')}-{data.get('budgetMax', '')}"
                    if data.get("budgetMin") is not None and data.get("budgetMin") != ""
                    and data.get("budgetMax") is not None and data.get("budgetMax") != ""
                    else ""
                ),
            }
            print(f"Formatted user_data: {user_data}")
        except Exception as format_error:
            print(f"Error formatting user data: {format_error}")
            return jsonify({"status": "error", "message": f"Error formatting data: {str(format_error)}"}), 400

        # If session_id exists and is valid, update it; otherwise create new one
        try:
            if session_id and session_id in user_sessions:
                user_sessions[session_id]["user_data"] = user_data
                print(f"Updated existing session: {session_id}")
            else:
                # Generate a new session ID if none provided or invalid
                session_id = f"session_{len(user_sessions) + 1}"
                user_sessions[session_id] = {"user_data": user_data}
                print(f"Created new session: {session_id}")
        except Exception as session_error:
            print(f"Error managing session: {session_error}")
            return jsonify({"status": "error", "message": f"Error managing session: {str(session_error)}"}), 500

        print(f"User data stored for session {session_id}: {user_data}")
        print(f"Total sessions after storing user info: {len(user_sessions)}")
        print(f"Session keys: {list(user_sessions.keys())}")

        # Improved terminal log to reflect all user info fields clearly
        print("User location:", user_data["user_location"])
        print("User profile details:")
        print("Age:", user_data["age"])
        print("Gender:", user_data["gender"])
        print("Budget range:", user_data["budget_range"])
        print(
            "Favorite product categories:", ", ".join(user_data["favorite_categories"])
        )
        print("Interests or hobbies:", user_data["interests"])

        return jsonify(
            {
                "status": "success",
                "message": "User information stored successfully",
                "session_id": session_id,
            }
        )
    except Exception as e:
        print(f"Error storing user info: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500


# Helper function to get currency symbol based on user location
def get_currency_symbol(location):
    """Get currency symbol based on location"""
    currency_map = {
        "United States": "$",
        "United Kingdom": "£",
        "Canada": "$",
        "Australia": "$",
        "Germany": "€",
        "France": "€",
        "Italy": "€",
        "Spain": "€",
        "Netherlands": "€",
        "Belgium": "€",
        "Austria": "€",
        "Switzerland": "CHF",
        "Japan": "¥",
        "India": "₹",
        "Brazil": "R$",
        "Mexico": "$",
        "South Korea": "₩",
        "Singapore": "$",
        "Hong Kong": "$",
        "Taiwan": "$",
    }
    return currency_map.get(location, "$")


def parse_ai_recommendations(sorted_products_text):
    """Parse AI recommendations text into structured product objects"""
    import re

    # Extract product details using regex
    product_pattern = r"Product: (.*?)\nURL: (.*?)\nPrice: [£$€]?([\d.,]+)\nRating: ([\d.]+)\nImage URL: (.*?)\nReasoning: (.*?)(?=\n\nProduct:|$)"
    matches = re.finditer(product_pattern, sorted_products_text, re.DOTALL)

    ai_recommendations = []
    for match in matches:
        name, url, price_str, rating, image, reasoning = match.groups()

        # Clean price string
        price_clean = price_str.replace(",", "").strip()
        try:
            price = float(price_clean)
        except ValueError:
            price = 0.0

        product = {
            "title": name.strip(),
            "url": url.strip(),
            "price": price,
            "rating": float(rating.strip()),
            "image_url": image.strip(),
            "reasoning": reasoning.strip(),
        }
        ai_recommendations.append(product)

    return ai_recommendations


@app.route("/api/shopping-recommendations", methods=["POST", "OPTIONS"])
def get_shopping_recommendations():
    """Get product recommendations based on user input and stored user data"""
    if request.method == "OPTIONS":
        # Handle preflight request
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Session-Id")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response
        
    try:
        # Debug: Log request details
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request content type: {request.content_type}")
        print(f"Request content length: {request.content_length}")
        
        # Check if request has JSON content
        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({
                "status": "error", 
                "message": "Content-Type must be application/json",
                "received_content_type": request.content_type
            }), 415
        
        data = request.get_json()
        if data is None:
            print("Error: Failed to parse JSON data")
            return jsonify({
                "status": "error", 
                "message": "Invalid JSON data"
            }), 400
            
        session_id = data.get("session_id")
        print(f"Received session_id: {session_id}")
        print(f"Available sessions: {list(user_sessions.keys())}")
        print(f"Full request data: {data}")

        if not session_id or session_id not in user_sessions:
            print(f"Session validation failed. session_id: {session_id}, exists: {session_id in user_sessions if session_id else False}")
            return jsonify({"status": "error", "message": "Invalid session"}), 400

        # Check if request is already being processed
        with processing_lock:
            if session_id in active_requests:
                return jsonify({"status": "processing", "message": "Request already being processed"}), 202
            
            # Mark request as active
            active_requests[session_id] = True

        try:
            # Submit request to worker pool for concurrent processing
            future = worker_pool.submit(process_recommendation_request, data)
            
            # Wait for result with reduced timeout for faster response
            try:
                result = future.result(timeout=45)  # Reduced from 60 to 45 seconds
                
                # Remove from active requests
                with processing_lock:
                    if session_id in active_requests:
                        del active_requests[session_id]
                
                # Return result
                if isinstance(result, tuple):
                    return jsonify(result[0]), result[1]
                else:
                    return jsonify(result)
                    
            except Exception as e:
                # Remove from active requests on error
                with processing_lock:
                    if session_id in active_requests:
                        del active_requests[session_id]
                
                print(f"Error in concurrent processing: {e}")
                return jsonify({"status": "error", "message": "Request processing failed"}), 500
                
        except Exception as e:
            # Remove from active requests on error
            with processing_lock:
                if session_id in active_requests:
                    del active_requests[session_id]
            
            print(f"Error submitting to worker pool: {e}")
            return jsonify({"status": "error", "message": "Failed to process request"}), 500

    except Exception as e:
        print(f"Main error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/export-data/<session_id>", methods=["GET"])
def export_user_data(session_id):
    """Export user data for download"""
    try:
        if session_id not in user_sessions:
            return jsonify({"status": "error", "message": "Invalid session"}), 400

        user_data = user_sessions[session_id]["user_data"]
        return jsonify({"status": "success", "data": user_data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/cleanup-session", methods=["POST"])
def cleanup_session():
    """Clean up a session when user closes the tab"""
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        
        if session_id and session_id in user_sessions:
            del user_sessions[session_id]
            print(f"Session cleaned up: {session_id}")
            return jsonify({
                "status": "success",
                "message": "Session cleaned up successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/request-status/<session_id>", methods=["GET"])
def get_request_status(session_id):
    """Check the status of a recommendation request"""
    try:
        with processing_lock:
            is_processing = session_id in active_requests
            has_results = session_id in user_sessions and "results" in user_sessions[session_id]
            
            if is_processing:
                return jsonify({
                    "status": "processing",
                    "message": "Request is being processed"
                })
            elif has_results:
                return jsonify({
                    "status": "completed",
                    "message": "Request completed successfully"
                })
            else:
                return jsonify({
                    "status": "idle",
                    "message": "No active request"
                })
                
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/cancel-request/<session_id>", methods=["POST"])
def cancel_request(session_id):
    """Cancel an active recommendation request"""
    try:
        with processing_lock:
            if session_id in active_requests:
                del active_requests[session_id]
                return jsonify({
                    "status": "success",
                    "message": "Request cancelled successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "No active request to cancel"
                }), 404
                
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/worker-stats", methods=["GET"])
def get_worker_stats():
    """Get statistics about the worker pool and active requests"""
    try:
        with processing_lock:
            stats = {
                "active_requests": len(active_requests),
                "active_request_sessions": list(active_requests.keys()),
                "worker_pool_size": worker_pool._max_workers,
                "total_sessions": len(user_sessions),
                "sessions_with_results": len([s for s in user_sessions.values() if "results" in s])
            }
            return jsonify({"status": "success", "stats": stats})
                
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def process_recommendation_request(request_data):
    """Process a single recommendation request concurrently"""
    session_id = request_data.get("session_id")
    shopping_input = request_data.get("shopping_input", {})
    
    # Detect environment
    ENV = os.getenv("ENV", "development").lower()
    IS_PRODUCTION = ENV == "production"

    try:
        print(f"Processing recommendation request for session: {session_id}")
        
        if session_id not in user_sessions:
            return {"status": "error", "message": "Invalid session"}, 400

        # Get user data from session
        user_data = user_sessions[session_id].get("user_data", {})
        
        if not user_data or not user_data.get("favorite_categories"):
            return {"status": "error", "message": "No user data found. Please complete your profile first."}, 400

        # Build user input string for Gemini prompt with enhanced brand focus
        preferred_brands = shopping_input.get('brandsPreferred', '').strip()
        brand_emphasis = ""
        if preferred_brands:
            brands_list = [brand.strip() for brand in preferred_brands.split(',') if brand.strip()]
            brand_emphasis = f"\nIMPORTANT: User specifically prefers these brands: {', '.join(brands_list)}"
            brand_emphasis += f"\nPlease prioritize products from these brands when possible."
        
        user_input = f"""
        Occasion: {shopping_input.get('occasion', '')}
        Preferred Brands: {preferred_brands}
        Shopping Request: {shopping_input.get('shoppingInput', '')}
        Favorite Categories: {', '.join(user_data.get('favorite_categories', []))}
        Interests or Hobbies: {user_data.get('interests', '')}
        {brand_emphasis}
        """

        # Get categories from Gemini
        categories = build_and_get_categories(
            GEMINI_API_KEY, user_input, user_data["user_location"], user_data
        )
        
        if not categories:
            return {"status": "error", "message": "Failed to get categories from Gemini API"}, 500

        # Filter and prioritize categories based on user request and brand preferences
        shopping_request = shopping_input.get('shoppingInput', '').lower()
        filtered_categories = []
        
        # Define keyword mappings for different types of requests
        category_keywords = {
            'music': ['music', 'song', 'album', 'artist', 'band', 'vinyl', 'cd', 'spotify', 'apple music', 'headphones', 'speaker', 'audio'],
            'gaming': ['game', 'gaming', 'console', 'controller', 'headset', 'pc gaming', 'playstation', 'xbox', 'nintendo'],
            'sports': ['sport', 'basketball', 'football', 'cricket', 'fitness', 'exercise', 'workout', 'training', 'athletic'],
            'tech': ['tech', 'technology', 'computer', 'laptop', 'phone', 'tablet', 'accessory', 'gadget', 'electronic'],
            'fashion': ['clothes', 'fashion', 'clothing', 'shirt', 'dress', 'shoes', 'sneakers', 'outfit', 'style'],
            'books': ['book', 'reading', 'novel', 'textbook', 'kindle', 'ebook', 'literature', 'author'],
            'home': ['home', 'kitchen', 'furniture', 'decor', 'appliance', 'garden', 'outdoor', 'household'],
            'automotive': ['car', 'automotive', 'vehicle', 'accessory', 'maintenance', 'parts', 'tools'],
            'beauty': ['beauty', 'makeup', 'skincare', 'cosmetic', 'perfume', 'lotion', 'cream'],
            'food': ['food', 'cooking', 'recipe', 'ingredient', 'snack', 'beverage', 'drink'],
            'pet': ['pet', 'dog', 'cat', 'animal', 'pet food', 'toy', 'accessory'],
            'baby': ['baby', 'infant', 'toddler', 'diaper', 'toy', 'clothing'],
            'office': ['office', 'work', 'desk', 'stationery', 'paper', 'pen', 'notebook'],
            'travel': ['travel', 'luggage', 'backpack', 'suitcase', 'trip', 'vacation'],
            'art': ['art', 'craft', 'painting', 'drawing', 'creative', 'diy', 'hobby']
        }
        
        # Determine the primary category based on user request
        primary_category = None
        category_scores = {}
        
        # Score each category based on keyword matches
        for category, keywords in category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in shopping_request:
                    score += 1
            if score > 0:
                category_scores[category] = score
        
        # Get the category with the highest score
        if category_scores:
            primary_category = max(category_scores, key=category_scores.get)
        else:
            # Try to extract keywords from the request for better matching
            request_words = shopping_request.split()
            
            # Check if any of the user's favorite categories match the request
            user_categories = user_data.get('favorite_categories', [])
            for user_cat in user_categories:
                if user_cat.lower() in shopping_request:
                    break
        
        # Enhanced category filtering with brand priority
        if preferred_brands and preferred_brands.strip():
            brands = [brand.strip().lower() for brand in preferred_brands.split(',') if brand.strip()]
            
            # First, prioritize categories that contain brand names
            brand_categories = []
            other_categories = []
            
            for category in categories:
                category_lower = category.lower()
                brand_found = False
                
                for brand in brands:
                    if brand in category_lower:
                        brand_categories.append(category)
                        brand_found = True
                        break
                
                if not brand_found:
                    other_categories.append(category)
            
            # If we found brand-specific categories, prioritize them
            if brand_categories:
                filtered_categories = brand_categories + other_categories
            else:
                # If no brand-specific categories, use primary category logic
                if primary_category:
                    primary_keywords = category_keywords[primary_category]
                    primary_categories = [cat for cat in categories if any(keyword in cat.lower() for keyword in primary_keywords)]
                    other_categories = [cat for cat in categories if not any(keyword in cat.lower() for keyword in primary_keywords)]
                    filtered_categories = primary_categories + other_categories
                else:
                    filtered_categories = categories
        else:
            # If no brands specified, use original logic
            if primary_category:
                primary_keywords = category_keywords[primary_category]
                primary_categories = [cat for cat in categories if any(keyword in cat.lower() for keyword in primary_keywords)]
                other_categories = [cat for cat in categories if not any(keyword in cat.lower() for keyword in primary_keywords)]
                filtered_categories = primary_categories + other_categories
            else:
                filtered_categories = categories

        # Process all categories for maximum variety - let Gemini select the best
        filtered_categories = filtered_categories
        
        # Clean category names for better scraping
        cleaned_categories = []
        for category in filtered_categories:
            # Remove bullet points and clean the category name
            clean_cat = category.replace("*", "").replace("  ", " ").strip()
            # Remove brand examples in parentheses
            clean_cat = re.sub(r'\s*\([^)]*\)', '', clean_cat)
            # Remove "e.g." and similar text
            clean_cat = re.sub(r'\s*e\.g\.,?\s*', '', clean_cat)
            clean_cat = clean_cat.strip()
            if clean_cat and len(clean_cat) > 2:
                cleaned_categories.append(clean_cat)
        
        categories = cleaned_categories

        # Get Amazon domain
        amazon_domain = get_amazon_domain(user_data["user_location"])

        # Dictionary to store category -> products
        category_products = {}

        def fetch_category_products(category):
            # Extract preferred brands from shopping input
            preferred_brands = shopping_input.get('brandsPreferred', '')
            
            # Get products directly from search results (much faster)
            scraped_products = amazon_category_top_products(
                category,
                amazon_domain,
                num_results=random.randint(3, 6),  # Variable number for better variety
                budget_range=user_data.get("budget_range"),
                preferred_brands=preferred_brands,  # Pass preferred brands to scraper
            )
            
            if not scraped_products:
                return category, []

            # Process and score the scraped products
            scored_products = []
            
            for product in scraped_products:
                if not product or not product.get('title'):
                    continue
                    
                # Enhanced brand filtering and scoring
                product_score = 0
                
                # Check if product title contains preferred brands
                if preferred_brands and preferred_brands.strip():
                    brands = [brand.strip().lower() for brand in preferred_brands.split(',') if brand.strip()]
                    product_title = product.get('title', '').lower()
                    
                    # Check brand matches in title
                    for brand in brands:
                        # Brand in title gets good score
                        if brand in product_title:
                            product_score += 10  # High score for brand match in title
                            break
                        # Partial brand match gets lower score
                        elif any(brand_word in product_title for brand_word in brand.split()):
                            product_score += 5  # Medium score for partial brand match
                            break
                
                # Filter products by budget range if price_value is available
                budget_range = user_data.get("budget_range")
                if budget_range and product.get("price_value") is not None:
                    try:
                        low, high = (
                            budget_range.replace("€", "")
                            .replace("$", "")
                            .replace("£", "")
                            .split("-")
                        )
                        low = float(low.strip())
                        high = float(high.strip())
                        if low <= product["price_value"] <= high:
                            # Add budget score (closer to middle of range gets higher score)
                            budget_mid = (low + high) / 2
                            price_diff = abs(product["price_value"] - budget_mid)
                            budget_score = max(0, 5 - (price_diff / budget_mid) * 5)
                            product_score += budget_score
                            scored_products.append((product, product_score))
                    except:
                        # If budget parsing fails, include product anyway
                        scored_products.append((product, product_score))
                else:
                    # If no price or budget, include product
                    scored_products.append((product, product_score))

            # Sort products by score (brand matches first, then by budget fit)
            scored_products.sort(key=lambda x: x[1], reverse=True)
            
            # Return only the product objects (without scores)
            return category, [product for product, score in scored_products]

        # --- PRODUCTION-ONLY LIMIT AND DELAY ---
        if IS_PRODUCTION:
            max_categories = 2  # Limit to 2 categories in production
            categories_to_process = categories[:max_categories]
        else:
            categories_to_process = categories

        for idx, category in enumerate(categories_to_process):
            category, products = fetch_category_products(category)
            category_products[category] = products
            # Add delay between category scrapes in production
            if IS_PRODUCTION and idx < len(categories_to_process) - 1:
                import time
                time.sleep(random.uniform(2, 3))  # 2-3 seconds delay

        # Gather all products
        all_products = []
        for products in category_products.values():
            all_products.extend(products)

        # Check if we have any real scraped products
        valid_products = [p for p in all_products if p and p.get("title") and p.get("url")]
        
        # Limit products for faster AI processing (top 6 products - reduced from 8)
        if len(valid_products) > 6:
            valid_products = valid_products[:6]
        
        # Get currency symbol (moved here to fix scope issue)
        currency_symbol = get_currency_symbol(user_data.get("user_location", ""))
        
        if not valid_products:
            print(f"No valid products found for session {session_id}, using fallback products")
            # Fallback to sample products based on the detected category
            fallback_products = generate_fallback_products(shopping_request, user_data)
            if fallback_products:
                # Format fallback products
                formatted_products = []
                for i, product in enumerate(fallback_products):
                    formatted_products.append({
                        "id": str(i + 1),
                        "name": product["title"],
                        "price": product.get("price_value", 0),
                        "currency": currency_symbol,
                        "image": product.get("image_url", "/placeholder.svg"),
                        "buyUrl": product.get("url", ""),
                        "category": "Sample",
                        "rating": product.get("rating", 4.0),
                        "reasoning": "Sample product based on your interests",
                    })
                
                response_data = {
                    "status": "success",
                    "categories": categories,
                    "products": formatted_products,
                    "ai_recommendations": json.dumps([]),
                    "note": "Using sample products due to temporary scraping issues"
                }
                
                user_sessions[session_id]["results"] = response_data
                return response_data
            else:
                return {"status": "error", "message": "Unable to fetch product recommendations at this time. Please try again later."}, 503

        # Now sort these products using the SortingAlgorithm
        sorting_algo = SortingAlgorithm(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            GEMINI_API_KEY,
        )

        try:
            # Get AI sorted recommendations
            sorted_products_text = sorting_algo.get_sorted_products(
                user_input, user_data, valid_products
            )

            # Parse AI recommendations
            ai_recommendations = parse_ai_recommendations(sorted_products_text)

            # Format products for frontend
            formatted_products = []

            # Create a mapping of scraped products by title for easy lookup
            scraped_products_map = {}
            for product in valid_products:
                if product and product.get("title"):
                    title_key = product["title"].strip().lower()
                    scraped_products_map[title_key] = product

            # Process AI recommendations and match with scraped data
            for i, ai_product in enumerate(ai_recommendations):
                ai_title = ai_product.get("title", "").strip()
                if not ai_title:
                    continue

                # Try to find matching scraped product
                scraped_product = None
                ai_title_key = ai_title.lower()

                # Exact match first
                if ai_title_key in scraped_products_map:
                    scraped_product = scraped_products_map[ai_title_key]
                else:
                    # Partial match
                    for scraped_title_key, product in scraped_products_map.items():
                        if (
                            ai_title_key in scraped_title_key
                            or scraped_title_key in ai_title_key
                        ):
                            scraped_product = product
                            break

                # Only add products that have real scraped data
                if scraped_product:
                    # Use scraped data as primary source
                    product_data = {
                        "id": str(i + 1),
                        "name": scraped_product["title"],
                        "price": scraped_product.get("price_value", 0),
                        "currency": currency_symbol,
                        "image": scraped_product.get("image_url", "/placeholder.svg"),
                        "buyUrl": scraped_product.get("url", ""),
                        "category": "Recommended",
                        "rating": 0,
                        "reasoning": ai_product.get("reasoning", "AI recommended product"),
                    }

                    # Parse rating from scraped data
                    if scraped_product.get("average_rating"):
                        try:
                            rating_str = str(scraped_product["average_rating"])
                            rating_clean = "".join(
                                c for c in rating_str if c.isdigit() or c == "."
                            )
                            if rating_clean:
                                scraped_rating = float(rating_clean)
                                product_data["rating"] = min(max(scraped_rating, 0), 5)
                        except:
                            pass

                    formatted_products.append(product_data)

            # If no AI recommendations matched with scraped data, use scraped products directly
            if not formatted_products and valid_products:
                # Limit to top 4 products for faster processing (reduced from 6)
                for i, product in enumerate(valid_products[:4]):
                    rating = 0
                    try:
                        rating_str = str(product.get("average_rating", "0"))
                        rating_clean = "".join(
                            c for c in rating_str if c.isdigit() or c == "."
                        )
                        if rating_clean:
                            rating = min(max(float(rating_clean), 0), 5)
                    except:
                        pass

                    formatted_products.append(
                        {
                            "id": str(i + 1),
                            "name": product["title"],
                            "price": product.get("price_value", 0) or 0,
                            "currency": currency_symbol,
                            "image": product.get("image_url", "/placeholder.svg"),
                            "buyUrl": product.get("url", ""),
                            "category": "General",
                            "rating": rating,
                            "reasoning": "Product recommendation based on your preferences",
                        }
                    )

            # Only return response if we have real products
            if not formatted_products:
                return {"status": "error", "message": "Unable to fetch product recommendations at this time. Please try again later."}, 503

            # Prepare response
            response_data = {
                "status": "success",
                "categories": categories,
                "products": formatted_products,
                "ai_recommendations": json.dumps(ai_recommendations),
            }

            user_sessions[session_id]["results"] = response_data
            return response_data

        except Exception as e:
            print(f"Error in AI processing: {e}")

            # Only use scraped products if they exist and are valid
            if valid_products:
                fallback_products = []
                # Limit to top 4 products for faster processing (reduced from 6)
                for i, product in enumerate(valid_products[:4]):
                    rating = 0
                    try:
                        rating_str = str(product.get("average_rating", "0"))
                        rating_clean = "".join(
                            c for c in rating_str if c.isdigit() or c == "."
                        )
                        if rating_clean:
                            rating = min(max(float(rating_clean), 0), 5)
                    except:
                        pass

                    fallback_products.append(
                        {
                            "id": str(i + 1),
                            "name": product["title"],
                            "price": product.get("price_value", 0) or 0,
                            "currency": currency_symbol,
                            "image": product.get("image_url", "/placeholder.svg"),
                            "buyUrl": product.get("url", ""),
                            "category": "General",
                            "rating": rating,
                            "reasoning": "Product recommendation based on your preferences",
                        }
                    )

                response_data = {
                    "status": "success",
                    "categories": categories,
                    "products": fallback_products,
                    "ai_recommendations": json.dumps([]),
                }

                user_sessions[session_id]["results"] = response_data
                return response_data
            else:
                # No valid products available
                return {"status": "error", "message": "Unable to fetch product recommendations at this time. Please try again later."}, 503

    except Exception as e:
        print(f"Error processing recommendation request: {e}")
        return {"status": "error", "message": str(e)}, 500


def generate_fallback_products(shopping_request, user_data):
    """Generate fallback sample products when scraping fails"""
    try:
        # Detect category from shopping request
        request_lower = shopping_request.lower()
        
        # Sample products by category
        sample_products = {
            'tech': [
                {
                    "title": "Wireless Bluetooth Headphones",
                    "price_value": 45.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.2
                },
                {
                    "title": "Smartphone Stand & Charger",
                    "price_value": 29.99,
                    "image_url": "/placeholder.svg", 
                    "url": "https://www.amazon.com",
                    "rating": 4.0
                },
                {
                    "title": "Portable Power Bank 10000mAh",
                    "price_value": 24.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.3
                }
            ],
            'sports': [
                {
                    "title": "Running Shoes - Lightweight",
                    "price_value": 59.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.1
                },
                {
                    "title": "Fitness Tracker Watch",
                    "price_value": 39.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.0
                },
                {
                    "title": "Yoga Mat - Non-Slip",
                    "price_value": 19.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.4
                }
            ],
            'gaming': [
                {
                    "title": "Gaming Mouse - RGB",
                    "price_value": 34.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.2
                },
                {
                    "title": "Mechanical Gaming Keyboard",
                    "price_value": 49.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.1
                },
                {
                    "title": "Gaming Headset with Mic",
                    "price_value": 39.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.0
                }
            ],
            'music': [
                {
                    "title": "Bluetooth Speaker - Portable",
                    "price_value": 35.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.3
                },
                {
                    "title": "Guitar Tuner - Digital",
                    "price_value": 15.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.1
                },
                {
                    "title": "Studio Headphones",
                    "price_value": 49.99,
                    "image_url": "/placeholder.svg",
                    "url": "https://www.amazon.com",
                    "rating": 4.2
                }
            ]
        }
        
        # Determine which category to use
        if any(word in request_lower for word in ['tech', 'technology', 'electronic', 'computer', 'phone']):
            return sample_products.get('tech', [])
        elif any(word in request_lower for word in ['sport', 'fitness', 'running', 'exercise', 'workout']):
            return sample_products.get('sports', [])
        elif any(word in request_lower for word in ['game', 'gaming', 'console', 'controller']):
            return sample_products.get('gaming', [])
        elif any(word in request_lower for word in ['music', 'audio', 'sound', 'speaker']):
            return sample_products.get('music', [])
        else:
            # Default to tech if no specific category detected
            return sample_products.get('tech', [])
            
    except Exception as e:
        print(f"Error generating fallback products: {e}")
        return []


if __name__ == "__main__":
    print("Starting Shopping Recommendation API...")
    print("API will be available at: https://eventually-yours-shopping-app-backend.onrender.com/")
    print("Health check: https://eventually-yours-shopping-app-backend.onrender.com/api/health")
    app.run(debug=True, host="0.0.0.0", port=5000)
