import random
import time
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, urlparse
import requests
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Global session pool for better connection reuse
session_pool = {}
session_lock = threading.Lock()

def get_session():
    """Get or create a session for the current thread"""
    thread_id = threading.get_ident()
    with session_lock:
        if thread_id not in session_pool:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            })
            session_pool[thread_id] = session
        return session_pool[thread_id]

def cleanup_session():
    """Clean up session for current thread"""
    thread_id = threading.get_ident()
    with session_lock:
        if thread_id in session_pool:
            del session_pool[thread_id]

def get_realistic_headers():
    """Generate realistic browser headers to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    
    accept_languages = [
        "en-GB,en-US;q=0.9,en;q=0.8",
        "en-US,en;q=0.9,en-GB;q=0.8",
        "en-CA,en-US;q=0.9,en;q=0.8",
        "en-AU,en-US;q=0.9,en;q=0.8",
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": random.choice(accept_languages),
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def create_brand_specific_search_url(amazon_domain, category, brand, budget_range=None):
    """
    Create a brand-specific Amazon search URL for better targeting
    """
    try:
        # Ensure amazon_domain has proper scheme
        if not amazon_domain.startswith('http'):
            amazon_domain = f"https://{amazon_domain}"
        
        # Create brand-specific search query
        search_query = f"{brand} {category}"
        encoded_query = quote_plus(search_query)
        
        # Build base search URL
        search_url = f"{amazon_domain}/s?k={encoded_query}&ref=sr_pg_1"
        
        # Add brand filter
        brand_filter = f"&rh=p_89%3A{quote_plus(brand)}"
        search_url += brand_filter
        
        # Add budget filter if provided
        if budget_range:
            try:
                low, high = budget_range.replace("€", "").replace("$", "").replace("£", "").split("-")
                low = float(low.strip())
                high = float(high.strip())
                search_url += f"&rh=p_36%3A{int(low*100)}-{int(high*100)}"
            except:
                pass  # Continue without budget filter if parsing fails
        
        return search_url
        
    except Exception as e:
        print(f"Error creating brand-specific search URL: {e}")
        return None


def amazon_category_top_products(category, amazon_domain, num_results=3, budget_range=None, preferred_brands=None):
    """
    Get top products from Amazon category search with optimized performance and brand integration
    """
    try:
        print(f"Searching for category: {category} on {amazon_domain}")
        if preferred_brands:
            print(f"Preferred brands: {preferred_brands}")
        
        # Use realistic headers to avoid detection
        headers = get_realistic_headers()
        
        # Ensure amazon_domain has proper scheme
        if not amazon_domain.startswith('http'):
            amazon_domain = f"https://{amazon_domain}"
        
        # Optimized search strategy: limit to 2-3 most effective searches
        search_urls = []
        
        # If brands are specified, create only the most effective brand-specific search
        if preferred_brands and preferred_brands.strip():
            brands = [brand.strip() for brand in preferred_brands.split(',') if brand.strip()]
            
            # Only use the first brand for maximum efficiency
            if brands:
                brand = brands[0]
                brand_url = create_brand_specific_search_url(amazon_domain, category, brand, budget_range)
                if brand_url:
                    search_urls.append((f"{brand} {category}", brand_url))
        
        # Always include the original category search (most reliable)
        search_urls.append((category, None))
        
        # Limit to maximum 2 searches for speed
        search_urls = search_urls[:2]
        
        all_product_urls = []
        seen_urls = set()
        
        # Use concurrent requests for faster processing
        def fetch_search_results(search_query, prebuilt_url):
            print(f"Searching with query: {search_query}")
            
            # Use prebuilt URL if available, otherwise build it
            if prebuilt_url:
                search_url = prebuilt_url
            else:
                # Build search URL
                encoded_query = quote_plus(search_query)
                search_url = f"{amazon_domain}/s?k={encoded_query}&ref=sr_pg_1"
                
                # Add budget filter if provided
                if budget_range:
                    try:
                        low, high = budget_range.replace("€", "").replace("$", "").replace("£", "").split("-")
                        low = float(low.strip())
                        high = float(high.strip())
                        search_url += f"&rh=p_36%3A{int(low*100)}-{int(high*100)}"
                    except:
                        pass
                
                # Add brand filter if we have specific brands
                if preferred_brands and preferred_brands.strip() and not prebuilt_url:
                    brands = [brand.strip() for brand in preferred_brands.split(',') if brand.strip()]
                    if brands:
                        brand_filter = "&rh=p_89%3A" + "%7C".join([quote_plus(brand) for brand in brands[:2]])
                        search_url += brand_filter
            
            print(f"Search URL: {search_url}")
            
            # Reduced retry attempts for speed
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = requests.get(search_url, headers=headers, timeout=10)  # Reduced timeout
                    
                    if response.status_code == 503:
                        print(f"503 error on attempt {attempt + 1} for {search_query}, retrying...")
                        if attempt < max_retries - 1:
                            time.sleep(random.uniform(1, 2))  # Reduced delay
                            continue
                        else:
                            print(f"Max retries reached for {search_query}, skipping...")
                            return []
                    
                    response.raise_for_status()
                    break
                    
                except requests.exceptions.RequestException as e:
                    print(f"Request error on attempt {attempt + 1} for {search_query}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(0.5, 1))  # Reduced delay
                        continue
                    else:
                        print(f"Max retries reached for {search_query}, skipping...")
                        return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Optimized product extraction with fewer selectors
            product_selectors = [
                'a[href*="/dp/"]',
                '.s-result-item a[href*="/dp/"]',
                '[data-component-type="s-search-result"] a[href*="/dp/"]'
            ]
            
            product_urls = []
            
            for selector in product_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    if href and '/dp/' in href:
                        # Clean and normalize URL
                        if href.startswith('/'):
                            full_url = urljoin(amazon_domain, href)
                        else:
                            full_url = href
                        
                        # Extract product ID and create clean URL
                        product_id_match = re.search(r'/dp/([A-Z0-9]{10})', full_url)
                        if product_id_match:
                            product_id = product_id_match.group(1)
                            clean_url = f"{amazon_domain}/dp/{product_id}"
                            
                            if clean_url not in seen_urls:
                                seen_urls.add(clean_url)
                                product_urls.append(clean_url)
                                
                                if len(product_urls) >= num_results * 2:  # Get more products for better selection
                                    break
                
                if len(product_urls) >= num_results * 2:
                    break
            
            return product_urls
        
        # Execute searches concurrently for better performance
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(fetch_search_results, search_query, prebuilt_url)
                for search_query, prebuilt_url in search_urls
            ]
            
            for future in as_completed(futures):
                try:
                    product_urls = future.result()
                    all_product_urls.extend(product_urls)
                    
                    # If we have enough products, stop waiting for other searches
                    if len(all_product_urls) >= num_results * 3:
                        break
                        
                except Exception as e:
                    print(f"Error in concurrent search: {e}")
        
        print(f"Found {len(all_product_urls)} total product URLs for category: {category}")
        
        # Return optimized number of products
        return all_product_urls[:num_results * 2]
        
    except Exception as e:
        print(f"Error in amazon_category_top_products for {category}: {e}")
        return []


def parse_price_to_float(price_str):
    if not price_str:
        return None
    
    # Remove currency symbols and clean the string
    cleaned = price_str.replace("£", "").replace("€", "").replace("$", "").replace(",", "").strip()
    
    # Handle different price formats
    if "p" in cleaned.lower():  # UK pence format
        # Convert pence to pounds
        pence_match = re.search(r"(\d+)p", cleaned.lower())
        if pence_match:
            pence = int(pence_match.group(1))
            return pence / 100.0
    
    # Handle decimal prices
    decimal_match = re.search(r"(\d+\.\d+)", cleaned)
    if decimal_match:
        return float(decimal_match.group(1))
    
    # Handle whole number prices
    whole_match = re.search(r"(\d+)", cleaned)
    if whole_match:
        return float(whole_match.group(1))
    
    return None


def scrape_amazon_product(url):
    """
    Scrape individual Amazon product page with optimized performance and brand detection
    """
    try:
        print(f"Scraping product: {url}")
        
        # Use realistic headers to avoid detection
        headers = get_realistic_headers()
        
        # Reduced retry attempts for speed
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=8)  # Reduced timeout
                
                if response.status_code == 503:
                    print(f"503 error on attempt {attempt + 1} for {url}, retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(1, 2))  # Reduced delay
                        continue
                    else:
                        print(f"Max retries reached for {url}, returning None")
                        return None
                
                response.raise_for_status()
                break
                
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1} for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(0.5, 1))  # Reduced delay
                    continue
                else:
                    print(f"Max retries reached for {url}, returning None")
                    return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product information with optimized selectors
        product_data = {}
        
        # Title extraction with optimized selectors
        title_selectors = [
            '#productTitle',
            'h1.a-size-large',
            'span#productTitle',
            'h1[data-automation-id="product-title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                product_data['title'] = title_elem.get_text().strip()
                break
        
        # Quick brand extraction from title (simplified for speed)
        if product_data.get('title'):
            title = product_data['title']
            
            # Simple brand detection: first capitalized word(s) at start
            brand_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', title)
            if brand_match:
                detected_brand = brand_match.group(1).strip()
                # Filter out common non-brand words
                if detected_brand.lower() not in ['the', 'new', 'best', 'top', 'premium', 'quality']:
                    product_data['detected_brand'] = detected_brand
        
        # Price extraction with optimized selectors
        price_selectors = [
            '.a-price-whole',
            '.a-price .a-offscreen',
            '#priceblock_ourprice'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text().strip()
                # Extract numeric price
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        product_data['price_value'] = float(price_match.group().replace(',', ''))
                        product_data['price'] = price_text
                        break
                    except ValueError:
                        continue
        
        # Image extraction with optimized selectors
        image_selectors = [
            '#landingImage',
            '.a-dynamic-image',
            'img#imgBlkFront'
        ]
        
        for selector in image_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-old-hires')
                if img_src:
                    product_data['image_url'] = img_src
                    break
        
        # Quick rating extraction
        rating_elem = soup.select_one('.a-icon-alt')
        if rating_elem:
            rating_text = rating_elem.get_text().strip()
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                try:
                    product_data['average_rating'] = float(rating_match.group(1))
                except ValueError:
                    pass
        
        # Add URL to product data
        product_data['url'] = url
        
        # Validate that we have at least a title
        if not product_data.get('title'):
            print(f"No title found for product: {url}")
            return None
        
        print(f"Successfully scraped product: {product_data.get('title', 'Unknown')}")
        if product_data.get('detected_brand'):
            print(f"Detected brand: {product_data.get('detected_brand')}")
        
        # Minimal delay to avoid rate limiting
        time.sleep(random.uniform(0.1, 0.3))  # Significantly reduced delay
        
        return product_data
        
    except Exception as e:
        print(f"Error scraping product {url}: {e}")
        return None


if __name__ == "__main__":
    # Example usage and test of amazon_scraper.py
    test_categories = [
        "laptop bags",
        "wireless headphones",
        "smart watches",
        "gaming chairs",
        "external hard drives",
        "coffee makers",
        "fitness trackers",
        "robot vacuum cleaners",
        "electric toothbrushes",
        "portable chargers",
    ]
    test_domain = "amazon.com"

    for category in test_categories:
        # print(f"\nFetching top products for category '{category}' on {test_domain}...")
        top_urls = amazon_category_top_products(category, test_domain, num_results=3)
        # print("Top product URLs:")
        for url in top_urls:
            pass  # Add your logic here
            # print(url)

        # if top_urls:
        #     # print("\nScraping product details for top products:")
        for url in top_urls:
            product_info = scrape_amazon_product(url)
            print(product_info)
