import random
import time
import httpx
from bs4 import BeautifulSoup       
from urllib.parse import quote_plus
import requests
import re
import threading
import json
from typing import List, Dict, Optional, Tuple

# Global rate limiting for concurrent requests
_request_lock = threading.Lock()
_last_request_time = 0
_min_request_interval = 2.0  # Increased to 2 seconds for better reliability

# Session management for better reliability
_session_cache = {}
_session_lock = threading.Lock()

def _get_session(domain: str) -> requests.Session:
    """Get or create a session for a specific domain with persistent cookies"""
    with _session_lock:
        if domain not in _session_cache:
            session = requests.Session()
            
            # Enhanced headers that look more like a real browser
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9,en-GB;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            })
            
            _session_cache[domain] = session
            
        return _session_cache[domain]


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


def _detect_bot_protection(soup: BeautifulSoup) -> bool:
    """Detect if Amazon is showing bot protection page"""
    page_text = soup.get_text().lower()
    bot_indicators = [
        "robot", "captcha", "blocked", "unusual", "verify", "security check",
        "enter the characters you see below", "type the characters you see",
        "to discuss automated access", "automated requests"
    ]
    return any(indicator in page_text for indicator in bot_indicators)


def _extract_products_from_page(soup: BeautifulSoup, domain: str) -> List[Dict]:
    """Extract product data from Amazon search results page"""
    products = []
    
    # Multiple selectors for product containers
    product_selectors = [
        "[data-component-type='s-search-result']",
        ".s-result-item",
        "[data-asin]"
    ]
    
    product_containers = []
    for selector in product_selectors:
        containers = soup.select(selector)
        if containers:
            product_containers = containers[:12]  # Limit to first 12
            break
    
    for container in product_containers:
        try:
            # Extract product URL
            link_selectors = [
                "a.a-link-normal.s-no-outline",
                "a[href*='/dp/']",
                "h2 a",
                "a[data-cy='title-recipe-link']"
            ]
            
            link_elem = None
            for selector in link_selectors:
                link_elem = container.select_one(selector)
                if link_elem:
                    break
            
            if not link_elem:
                continue
                
            href = link_elem.get("href")
            if not href or "/dp/" not in href:
                continue
            
            # Clean URL
            if href.startswith("/"):
                full_url = f"https://www.{domain}{href.split('?')[0]}"
            elif href.startswith("http"):
                full_url = href.split('?')[0]
            else:
                continue
            
            # Extract title
            title_selectors = [
                "h2 a span",
                "h2 span",
                ".a-text-normal",
                "span.a-size-base-plus"
            ]
            
            title = None
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 5:
                        break
            
            if not title:
                continue
            
            # Extract price
            price_selectors = [
                ".a-price .a-offscreen",
                ".a-price-whole",
                ".a-price .a-price-whole",
                ".a-price-range .a-offscreen"
            ]
            
            price_text = None
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text:
                        break
            
            price_value = parse_price_to_float(price_text)
            
            # Extract rating
            rating_selectors = [
                "span.a-icon-alt",
                ".a-icon-star-small .a-icon-alt",
                "i.a-icon-star .a-icon-alt"
            ]
            
            rating = None
            for selector in rating_selectors:
                rating_elem = container.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                            break
                        except ValueError:
                            continue
            
            # Extract image
            img_selectors = [
                "img.s-image",
                "img[data-image-latency='s-product-image']",
                "img[src*='images']"
            ]
            
            image_url = None
            for selector in img_selectors:
                img_elem = container.select_one(selector)
                if img_elem and img_elem.has_attr("src"):
                    image_url = img_elem.get("src")
                    if image_url and "data:image" not in image_url:
                        break
            
            # Only add if we have essential data
            if title and full_url:
                product_data = {
                    "url": full_url,
                    "title": title,
                    "image_url": image_url,
                    "price": price_text,
                    "price_value": price_value,
                    "average_rating": rating,
                }
                products.append(product_data)
                
        except Exception as e:
            continue  # Skip this product if there's an error
    
    return products


def _make_request_with_retry(url: str, domain: str, max_retries: int = 3) -> Tuple[Optional[requests.Response], str]:
    """Make a request with retry logic and better error handling"""
    session = _get_session(domain)
    
    for attempt in range(max_retries):
        try:
            # Apply rate limiting
            _rate_limit_request()
            
            # Add random delay between attempts
            if attempt > 0:
                delay = random.uniform(3, 6) * (attempt + 1)  # Exponential backoff
                time.sleep(delay)
            
            # Add referer for subsequent attempts
            if attempt > 0:
                session.headers.update({
                    "Referer": f"https://www.{domain}/"
                })
            
            # Make request with timeout
            response = session.get(url, timeout=10)
            
            # Check for specific error codes
            if response.status_code == 503:
                return None, f"503 Server Error (attempt {attempt + 1}/{max_retries})"
            elif response.status_code == 429:
                return None, f"429 Rate Limited (attempt {attempt + 1}/{max_retries})"
            elif response.status_code == 403:
                return None, f"403 Forbidden (attempt {attempt + 1}/{max_retries})"
            elif response.status_code != 200:
                return None, f"HTTP {response.status_code} (attempt {attempt + 1}/{max_retries})"
            
            # Check for bot protection
            soup = BeautifulSoup(response.text, "html.parser")
            if _detect_bot_protection(soup):
                return None, f"Bot detection (attempt {attempt + 1}/{max_retries})"
            
            return response, "success"
            
        except requests.exceptions.Timeout:
            return None, f"Timeout (attempt {attempt + 1}/{max_retries})"
        except requests.exceptions.ConnectionError:
            return None, f"Connection Error (attempt {attempt + 1}/{max_retries})"
        except Exception as e:
            return None, f"Request Error: {str(e)} (attempt {attempt + 1}/{max_retries})"
    
    return None, f"All {max_retries} attempts failed"


def amazon_category_top_products(
    category: str, 
    amazon_domain: str, 
    num_results: int = 4, 
    budget_range: Optional[str] = None, 
    preferred_brands: Optional[str] = None
) -> List[Dict]:
    """
    Ultra-reliable Amazon scraper with comprehensive error handling and fallback strategies
    """
    print(f"Searching for category: {category} on {amazon_domain}")
    if preferred_brands:
        print(f"Preferred brands: {preferred_brands}")

    # Parse budget range
    low_price = None
    high_price = None
    if budget_range:
        try:
            parts = budget_range.replace("£", "").replace("€", "").replace("$", "").split("-")
            if len(parts) == 2:
                low_price = parts[0].strip()
                high_price = parts[1].strip()
        except Exception:
            print("Error parsing budget range")

    # Clean domain
    domain = amazon_domain.replace("www.", "")
    
    # Build search query
    search_query = category
    if preferred_brands and preferred_brands.strip():
        brands = [brand.strip() for brand in preferred_brands.split(',') if brand.strip()]
        if brands:
            search_query = f"{brands[0]} {category}"

    # Add price filters
    price_filter = ""
    if low_price and high_price:
        price_filter = f"&low-price={low_price}&high-price={high_price}"

    # Multiple search strategies with different approaches
    search_strategies = [
        {
            "name": "best-sellers",
            "url": f"https://www.{domain}/s?k={quote_plus(search_query)}&s=best-sellers{price_filter}",
            "priority": 1
        },
        {
            "name": "review-rank", 
            "url": f"https://www.{domain}/s?k={quote_plus(search_query)}&s=review-rank{price_filter}",
            "priority": 2
        },
        {
            "name": "price-low-to-high",
            "url": f"https://www.{domain}/s?k={quote_plus(search_query)}&s=price-asc-rank{price_filter}",
            "priority": 3
        },
        {
            "name": "default",
            "url": f"https://www.{domain}/s?k={quote_plus(search_query)}{price_filter}",
            "priority": 4
        }
    ]

    all_products = []
    
    for strategy in search_strategies:
        strategy_name = strategy["name"]
        search_url = strategy["url"]
        
        print(f"Trying {strategy_name} strategy: {search_url}")
        
        response, status = _make_request_with_retry(search_url, domain, max_retries=2)
        
        if response is None:
            print(f"❌ {status} for {category} ({strategy_name} strategy)")
            continue
        
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            products = _extract_products_from_page(soup, domain)
            
            if products:
                print(f"✅ Found {len(products)} products with {strategy_name} strategy")
                # Log detailed product information
                for i, product in enumerate(products, 1):
                    print(f"   {i}. {product.get('title', 'No title')}")
                    print(f"      Price: {product.get('price', 'No price')}")
                    print(f"      Rating: {product.get('average_rating', 'No rating')}")
                    print(f"      URL: {product.get('url', 'No URL')}")
                all_products.extend(products)
                
                # If we have enough products, stop trying more strategies
                if len(all_products) >= num_results * 2:  # Get extra products for variety
                    break
            else:
                print(f"No products found with {strategy_name} strategy")
                
        except Exception as e:
            print(f"Error processing {strategy_name} strategy: {str(e)}")
            continue

    # Remove duplicates and limit results
    unique_products = []
    seen_urls = set()
    
    for product in all_products:
        if product["url"] not in seen_urls:
            unique_products.append(product)
            seen_urls.add(product["url"])
            
            if len(unique_products) >= num_results:
                break
    
    if unique_products:
        print(f"✅ Successfully found {len(unique_products)} unique products for {category}")
        return unique_products
    else:
        print(f"No products found for {category} with any strategy")
        return []


def parse_price_to_float(price_str: Optional[str]) -> Optional[float]:
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


def scrape_amazon_product(url: str) -> Optional[Dict]:
    """Scrape detailed product information from Amazon product page"""
    try:
        # Extract domain from URL
        domain = url.split("//")[1].split("/")[0].replace("www.", "")
        
        session = _get_session(domain)
        response = session.get(url, timeout=10)
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
        print(f"Error scraping product {url}: {str(e).strip()}")
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