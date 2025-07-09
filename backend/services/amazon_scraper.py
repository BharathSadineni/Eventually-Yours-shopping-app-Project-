import random
import time
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import requests
import re


def amazon_category_top_products(
    category, amazon_domain, num_results=10, budget_range=None, preferred_brands=None
):
    """
    Fast single-request Amazon scraper with enhanced anti-detection
    """
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

    # Try different search strategies with better anti-detection
    search_strategies = [
        f"https://www.{domain}/s?k={quote_plus(search_query)}&s=review-rank{price_filter}",
        f"https://www.{domain}/s?k={quote_plus(search_query)}&s=best-sellers{price_filter}",
        f"https://www.{domain}/s?k={quote_plus(search_query)}{price_filter}",
    ]

    for strategy_idx, search_url in enumerate(search_strategies):
        print(f"Trying search strategy {strategy_idx + 1}: {search_url}")
        
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
            
            # Random delay to avoid detection
            time.sleep(random.uniform(1, 2))
            
            response = session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Enhanced bot detection check
            page_text = soup.get_text().lower()
            if any(term in page_text for term in ["robot", "captcha", "blocked", "unusual", "verify"]):
                print(f"Bot detection detected for {category}")
                time.sleep(random.uniform(2, 4))  # Wait longer before next strategy
                continue  # Try next strategy

            # Extract all product data from search results in one go
            products = []
            
            # Find all product containers
            product_containers = soup.select("[data-component-type='s-search-result']")
            
            for container in product_containers[:num_results * 2]:  # Get more to filter
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
                    
                    # Extract rating
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
                        
                except Exception as e:
                    print(f"Error extracting product data: {e}")
                    continue
            
            if products:
                print(f"✅ Found {len(products)} products with strategy {strategy_idx + 1}")
                return products[:num_results]
            else:
                print(f"No products found with strategy {strategy_idx + 1}")
                continue
                    
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                print(f"503 Server Error for {category} (strategy {strategy_idx + 1})")
                time.sleep(random.uniform(3, 6))  # Wait longer for 503 errors
                continue  # Try next strategy
            else:
                print(f"HTTP Error {e.response.status_code} for {category}: {e}")
                continue
        except Exception as e:
            print(f"Amazon category scraping error: {e}")
            continue
    
    print(f"No products found for {category} with any strategy")
    return []


def parse_price_to_float(price_str):
    if not price_str:
        return None
    # Remove currency symbols and commas, extract numeric part
    match = re.search(r"[\d,.]+", price_str)
    if not match:
        return None
    num_str = match.group(0).replace(",", "").replace(".", "")
    # Handle decimal point by checking last two digits
    if len(num_str) > 2:
        num = float(num_str[:-2] + "." + num_str[-2:])
    else:
        num = float(num_str)
    return num


def scrape_amazon_product(url):
    """
    Individual product scraper (fallback for when search scraping doesn't work)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    
    try:
        # Very minimal delay
        time.sleep(random.uniform(0.1, 0.3))
        
        response = httpx.get(url, headers=headers, timeout=6)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find(id="productTitle")
    title = title.get_text(strip=True) if title else None

    image = soup.select_one("#imgTagWrapperId img")
    image_url = image["src"] if image and image.has_attr("src") else None

    price = soup.select_one(".a-price .a-offscreen")
    if not price:
        # Try alternative price selectors
        price = soup.select_one("#priceblock_ourprice") or soup.select_one(
            "#priceblock_dealprice"
        )
    price_text = price.get_text(strip=True) if price else None
    price_value = parse_price_to_float(price_text)

    rating_tag = soup.select_one("span.a-icon-alt")
    rating = None
    if rating_tag:
        rating_text = rating_tag.get_text(strip=True)
        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
        if rating_match:
            try:
                rating = float(rating_match.group(1))
            except ValueError:
                pass

    return {
        "url": url,
        "title": title,
        "image_url": image_url,
        "price": price_text,
        "price_value": price_value,
        "average_rating": rating,
    }


def test_amazon_scraper():
    """Test function to check if Amazon scraper is working"""
    print("Testing Amazon scraper...")
    
    # Test with a simple category
    test_category = "laptop"
    test_domain = "www.amazon.co.uk"
    
    print(f"Testing category: {test_category} on {test_domain}")
    
    # Try to get products directly
    products = amazon_category_top_products(test_category, test_domain, num_results=2)
    
    if not products:
        print("❌ Failed to get products - Amazon scraper is not working")
        return False
    
    print(f"✅ Got {len(products)} products")
    
    # Show first product details
    if products:
        product = products[0]
        print(f"✅ Successfully scraped product: {product.get('title', 'Unknown')}")
        print(f"  Price: {product.get('price', 'N/A')}")
        print(f"  Rating: {product.get('average_rating', 'N/A')}")
        return True
    
    return False


if __name__ == "__main__":
    # Test the scraper
    test_amazon_scraper()