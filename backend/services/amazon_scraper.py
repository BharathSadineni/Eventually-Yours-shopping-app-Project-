import random
import time
import httpx
from bs4 import BeautifulSoup       
from urllib.parse import quote_plus
import requests
import re
import threading

# Global rate limiting for concurrent requests
_request_lock = threading.Lock()
_last_request_time = 0
_min_request_interval = 1.5  # Minimum 1.5 seconds between requests


def _rate_limit_request():
    """Ensure minimum time between requests to avoid overwhelming Amazon"""
    global _last_request_time
    with _request_lock:
        current_time = time.time()
        time_since_last = current_time - _last_request_time
        if time_since_last < _min_request_interval:
            sleep_time = _min_request_interval - time_since_last
            time.sleep(sleep_time)
        _last_request_time = time.time()


def amazon_category_top_products(
    category, amazon_domain, num_results=4, budget_range=None, preferred_brands=None
):
    """
    Ultra-fast Amazon scraper optimized for speed with better anti-detection
    - Single request strategy
    - Minimal delays
    - Better anti-detection to reduce 503 errors
    - Rate limiting for concurrent requests
    - 15-second timeout per category
    """
    # Apply rate limiting for concurrent requests
    _rate_limit_request()
    
    # Set timeout for this category
    start_time = time.time()
    category_timeout = 15  # 15 seconds per category
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    ]

    print(f"Searching for category: {category} on {amazon_domain}")
    if preferred_brands:
        print(f"Preferred brands: {preferred_brands}")

    # Parse budget_range if provided
    low_price = None
    high_price = None
    if budget_range:
        try:
            parts = (
                budget_range.replace("£", "")
                .replace("€", "")
                .replace("$", "")
                .split("-")
            )
            if len(parts) == 2:
                low_price = parts[0].strip()
                high_price = parts[1].strip()
        except Exception:
            print("Error parsing budget range. Please check the format.")

    # Construct Amazon search URL for the category, sorted by review rank
    domain = amazon_domain
    if domain.startswith("www."):
        domain = domain[4:]

    # Build search query with brand preference if available
    search_query = category
    if preferred_brands and preferred_brands.strip():
        brands = [brand.strip() for brand in preferred_brands.split(',') if brand.strip()]
        if brands:
            # Add the first preferred brand to the search query
            search_query = f"{brands[0]} {category}"

    # Add price filters if available
    price_filter = ""
    if low_price and high_price:
        price_filter = f"&low-price={low_price}&high-price={high_price}"

    # Try different search strategies to avoid 503 errors
    search_strategies = [
        ("best-sellers", f"https://www.{domain}/s?k={quote_plus(search_query)}&s=best-sellers{price_filter}"),
        ("review-rank", f"https://www.{domain}/s?k={quote_plus(search_query)}&s=review-rank{price_filter}"),
        ("default", f"https://www.{domain}/s?k={quote_plus(search_query)}{price_filter}"),
    ]

    for strategy_idx, (strategy_name, search_url) in enumerate(search_strategies):
        # Check timeout before each strategy
        elapsed_time = time.time() - start_time
        if elapsed_time >= category_timeout:
            print(f"⏰ Category timeout reached for {category}, stopping search")
            break
            
        print(f"Trying {strategy_name} strategy: {search_url}")
        
        try:
            # Enhanced headers with better anti-detection
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,en-GB;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            }
            
            # Use session with persistent cookies
            session = requests.Session()
            session.headers.update(headers)
            
            # Add referer to look more natural
            if strategy_idx > 0:
                session.headers.update({
                    "Referer": f"https://www.{domain}/"
                })
            
            # Adaptive delay based on strategy and concurrent processing
            if strategy_idx == 0:
                time.sleep(random.uniform(0.5, 1.0))  # Slightly longer for concurrent safety
            else:
                time.sleep(random.uniform(1.0, 2.0))  # Longer for retries
            
            # Check timeout after delay
            elapsed_time = time.time() - start_time
            if elapsed_time >= category_timeout:
                print(f"⏰ Category timeout reached for {category} after delay")
                break
            
            # Fast timeout
            response = session.get(search_url, timeout=8)  # Increased timeout slightly
            
            # Check for 503 error specifically
            if response.status_code == 503:
                print(f"503 Server Error for {category} ({strategy_name} strategy)")
                time.sleep(random.uniform(3, 5))  # Wait longer for 503 errors
                continue
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Quick bot detection check
            page_text = soup.get_text().lower()
            if any(term in page_text for term in ["robot", "captcha", "blocked", "unusual", "verify", "security check"]):
                print(f"Bot detection detected for {category}")
                time.sleep(random.uniform(2, 3))  # Wait longer on detection
                continue

            # Extract product data efficiently
            products = []
            
            # Find all product containers - limit to first 12 for better variety
            product_containers = soup.select("[data-component-type='s-search-result']")[:12]
            
            for container in product_containers:
                # Check timeout during product extraction
                elapsed_time = time.time() - start_time
                if elapsed_time >= category_timeout:
                    print(f"⏰ Category timeout reached for {category} during product extraction")
                    break
                    
                try:
                    # Extract product URL
                    link_elem = container.select_one("a.a-link-normal.s-no-outline")
                    if not link_elem:
                        link_elem = container.select_one("a[href*='/dp/']")
                    
                    if not link_elem:
                        continue
                        
                    href = link_elem.get("href")
                    if not href or "/dp/" not in href:
                        continue
                    
                    # Clean URL
                    full_url = f"https://{domain}{href.split('?')[0]}"
                    if "www." not in full_url:
                        parts = full_url.split("//")
                        full_url = parts[0] + "//www." + parts[1]
                    
                    # Extract title
                    title_elem = container.select_one("h2 a span")
                    if not title_elem:
                        title_elem = container.select_one("h2 span")
                    title = title_elem.get_text(strip=True) if title_elem else None
                    
                    # Extract price
                    price_elem = container.select_one(".a-price .a-offscreen")
                    if not price_elem:
                        price_elem = container.select_one(".a-price-whole")
                    price_text = price_elem.get_text(strip=True) if price_elem else None
                    price_value = parse_price_to_float(price_text)
                    
                    # Extract rating (simplified)
                    rating_elem = container.select_one("span.a-icon-alt")
                    rating = None
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            try:
                                rating = float(rating_match.group(1))
                            except ValueError:
                                pass
                    
                    # Extract image
                    img_elem = container.select_one("img.s-image")
                    image_url = img_elem.get("src") if img_elem and img_elem.has_attr("src") else None
                    
                    # Only add if we have at least a title
                    if title:
                        product_data = {
                            "url": full_url,
                            "title": title,
                            "image_url": image_url,
                            "price": price_text,
                            "price_value": price_value,
                            "average_rating": rating,
                        }
                        products.append(product_data)
                        
                        # Stop if we have enough products
                        if len(products) >= num_results:
                            break
                        
                except Exception as e:
                    print(f"Error extracting product data: {e}")
                    continue
            
            if products:
                print(f"✅ Found {len(products)} products with {strategy_name} strategy")
                return products[:num_results]
            else:
                print(f"No products found with {strategy_name} strategy")
                continue
                    
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                print(f"503 Server Error for {category} ({strategy_name} strategy)")
                time.sleep(random.uniform(3, 5))  # Wait longer for 503 errors
                continue
            else:
                print(f"HTTP Error {e.response.status_code} for {category}: {e}")
                continue
        except requests.exceptions.Timeout:
            print(f"Timeout for {category} ({strategy_name} strategy)")
            continue
        except Exception as e:
            print(f"Amazon category scraping error: {e}")
            continue

    print(f"No products found for {category} with any strategy")
    return []


def parse_price_to_float(price_str):
    """Parse price string to float value"""
    if not price_str:
        return None
    
    try:
        # Remove currency symbols and commas
        cleaned_price = re.sub(r'[£$€,]', '', price_str.strip())
        # Extract the first number (before any additional text)
        price_match = re.search(r'(\d+\.?\d*)', cleaned_price)
        if price_match:
            return float(price_match.group(1))
    except (ValueError, AttributeError):
        pass
    
    return None


def scrape_amazon_product(url):
    """Scrape detailed product information from Amazon product page"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract product details
        title_elem = soup.select_one("#productTitle")
        title = title_elem.get_text(strip=True) if title_elem else None
        
        price_elem = soup.select_one("#priceblock_ourprice, .a-price .a-offscreen")
        price_text = price_elem.get_text(strip=True) if price_elem else None
        price_value = parse_price_to_float(price_text)
        
        rating_elem = soup.select_one("#acrPopover")
        rating = None
        if rating_elem:
            rating_text = rating_elem.get("title", "")
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                except ValueError:
                    pass
        
        image_elem = soup.select_one("#landingImage, #imgBlkFront")
        image_url = image_elem.get("src") if image_elem and image_elem.has_attr("src") else None
        
        return {
            "url": url,
            "title": title,
            "image_url": image_url,
            "price": price_text,
            "price_value": price_value,
            "average_rating": rating,
        }
        
    except Exception as e:
        print(f"Error scraping product {url}: {e}")
        return None


def test_amazon_scraper():
    """Test the Amazon scraper with a simple category"""
    print("Testing Amazon scraper...")
    
    # Test with a simple category
    test_category = "headphones"
    test_domain = "amazon.com"
    
    products = amazon_category_top_products(
        test_category,
        test_domain,
        num_results=3,
        budget_range="20-100"
    )
    
    if products:
        print(f"✅ Successfully found {len(products)} products")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.get('title', 'No title')} - {product.get('price', 'No price')}")
    else:
        print("❌ No products found")
    
    return products


if __name__ == "__main__":
    test_amazon_scraper()