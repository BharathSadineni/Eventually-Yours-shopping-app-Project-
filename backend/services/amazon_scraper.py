import random
import time
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def amazon_category_top_products(
    category, amazon_domain, num_results=10, budget_range=None, preferred_brands=None
):
    """
    Scrape Amazon category page for top product URLs using rotating user agents and random delays to avoid blocking.
    Supports optional budget_range filtering in the format "$low-$high" and preferred_brands filtering.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
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

    search_url = (
        f"https://www.{domain}/s?k={quote_plus(search_query)}&s=review-rank{price_filter}"
    )

    print(f"Search URL: {search_url}")

    urls = []
    max_retries = 3
    retry_delay = 5
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            }
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Check if we got blocked or got an error page
            if "robot" in soup.get_text().lower() or "captcha" in soup.get_text().lower():
                print(f"Bot detection detected for {category}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay + random.uniform(0, 3))
                    continue
                else:
                    return []

            # Find product links in search results
            results = soup.select("a.a-link-normal.s-no-outline")
            for link in results:
                href = link.get("href")
                if href and "/dp/" in href:
                    full_url = f"https://{domain}{href.split('?')[0]}"
                    if full_url not in urls:
                        urls.append(full_url)
                    if len(urls) >= num_results:
                        break
            break  # success, exit retry loop
        except Exception as e:
            print(f"Amazon category scraping error: {e}")
            if attempt < max_retries - 1:
                delay = retry_delay + random.uniform(0, 3)
                print(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Moving on.")

    # Be polite and avoid hammering Amazon
    time.sleep(random.uniform(1, 3))

    # Clean URLs to ensure https and www prefix
    cleaned_urls = []
    for url in urls[:num_results]:
        if url.startswith("http://"):
            url = "https://" + url[len("http://") :]
        if "www." not in url:
            parts = url.split("//")
            url = parts[0] + "//www." + parts[1]
        cleaned_urls.append(url)

    print(f"Found {len(cleaned_urls)} product URLs for category: {category}")
    return cleaned_urls


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
    Scrape individual Amazon product page with enhanced error handling and brand detection
    """
    try:
        print(f"Scraping product: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Add retry logic for product scraping
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = httpx.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                break
            except Exception as e:
                print(f"Error fetching URL {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(1, 2))
                    continue
                else:
                    return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Check if we got blocked or got an error page
        if "robot" in soup.get_text().lower() or "captcha" in soup.get_text().lower():
            print(f"Bot detection detected for product: {url}")
            return None

        title = soup.find(id="productTitle")
        title = title.get_text(strip=True) if title else None

        # Quick brand extraction from title
        detected_brand = None
        if title:
            # Simple brand detection: first capitalized word(s) at start
            brand_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', title)
            if brand_match:
                detected_brand = brand_match.group(1).strip()
                # Filter out common non-brand words
                if detected_brand.lower() in ['the', 'new', 'best', 'top', 'premium', 'quality']:
                    detected_brand = None

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

        product_data = {
            "url": url,
            "title": title,
            "image_url": image_url,
            "price": price_text,
            "price_value": price_value,
            "average_rating": rating,
        }
        
        # Add detected brand if found
        if detected_brand:
            product_data["detected_brand"] = detected_brand

        # Validate that we have at least a title
        if not product_data.get('title'):
            print(f"No title found for product: {url}")
            return None

        print(f"Successfully scraped product: {product_data.get('title', 'Unknown')}")
        if detected_brand:
            print(f"Detected brand: {detected_brand}")

        # Minimal delay to avoid rate limiting
        time.sleep(random.uniform(0.1, 0.3))

        return product_data

    except Exception as e:
        print(f"Error scraping product {url}: {e}")
        return None


def test_amazon_scraper():
    """Test function to check if Amazon scraper is working"""
    print("Testing Amazon scraper...")
    
    # Test with a simple category
    test_category = "laptop"
    test_domain = "www.amazon.co.uk"
    
    print(f"Testing category: {test_category} on {test_domain}")
    
    # Try to get product URLs
    urls = amazon_category_top_products(test_category, test_domain, num_results=2)
    
    if not urls:
        print("❌ Failed to get product URLs - Amazon scraper is not working")
        return False
    
    print(f"✅ Got {len(urls)} product URLs")
    
    # Try to scrape one product
    if urls:
        product = scrape_amazon_product(urls[0])
        if product and product.get('title'):
            print(f"✅ Successfully scraped product: {product['title']}")
            return True
        else:
            print("❌ Failed to scrape product details")
            return False
    
    return False


if __name__ == "__main__":
    # Test the scraper
    test_amazon_scraper()