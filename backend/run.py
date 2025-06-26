import sys
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.domain_gen import get_amazon_domain
from services.amazon_scraper import amazon_category_top_products, scrape_amazon_product
from services.prompt_builder import build_and_get_categories


def get_user_details():
    """Collect user details manually through input prompts"""
    print("\nPlease enter your details:")
    user_input = input("Enter your shopping input: ").strip()
    user_location = input("Enter your location: ").strip()
    age = input("Enter your age: ").strip()
    gender = input("Enter your gender: ").strip()
    budget_range = input("Enter your budget range (e.g., 100-500): ").strip()
    favorite_categories = input(
        "Enter your favorite product categories (comma-separated): "
    ).strip()
    interests = input("Enter your interests or hobbies (comma-separated): ").strip()
    shopping_method = input(
        "Enter your preferred shopping method (online/in-store): "
    ).strip()

    # Create profile details dictionary
    profile_details = {
        "age": age,
        "gender": gender,
        "budget_range": budget_range,
        "favorite_product_categories": favorite_categories,
        "interests_or_hobbies": interests,
        "preferred_shopping_method": shopping_method,
        "user_location": user_location,
    }

    return user_input, profile_details


def main():
    # Get API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please create a .env file in the backend directory with your API key:")
        print("GEMINI_API_KEY=your_actual_api_key_here")
        return

    # Get user details manually
    user_input, profile_details = get_user_details()
    user_location = profile_details["user_location"]

    categories = build_and_get_categories(
        api_key, user_input, user_location, profile_details
    )
    if not categories:
        print("Failed to get categories from Gemini API.")
        return

    amazon_domain = get_amazon_domain(user_location)

    # Limit categories to top 7
    categories = categories[:7]

    # Dictionary to hold category and its products
    category_products = {}

    def fetch_category_products(category):
        urls = amazon_category_top_products(
            category,
            amazon_domain,
            num_results=3,
            budget_range=profile_details.get("budget_range"),
        )
        products = []
        if not urls:
            return category, products
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(scrape_amazon_product, url): url for url in urls}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    product = future.result()
                    if product:
                        # Filter products by budget range if price_value is available
                        budget_range = profile_details.get("budget_range")
                        if budget_range and product.get("price_value") is not None:
                            try:
                                low, high = (
                                    budget_range.replace("€", "")
                                    .replace("$", "")
                                    .split("-")
                                )
                                low = float(low.strip())
                                high = float(high.strip())
                                if low <= product["price_value"] <= high:
                                    products.append(product)
                            except Exception:
                                # If parsing fails, include product anyway
                                products.append(product)
                        else:
                            products.append(product)
                except Exception as e:
                    print(f"Exception occurred while scraping URL {url}: {e}")
        return category, products

    with ThreadPoolExecutor(max_workers=len(categories)) as category_executor:
        category_futures = [
            category_executor.submit(fetch_category_products, category)
            for category in categories
        ]
        for future in as_completed(category_futures):
            category, products = future.result()
            category_products[category] = products

    # Integrate sorting algorithm to get ordered product recommendations
    from sorting_algorithm import SortingAlgorithm

    sorting_algo = SortingAlgorithm(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        api_key,
    )
    all_products = []
    for products in category_products.values():
        all_products.extend(products)
    try:
        sorted_products_text = sorting_algo.get_sorted_products(
            user_input, profile_details, all_products
        )
        print("\nSorted product recommendations based on user preferences:\n")
        print(sorted_products_text)
    except Exception as e:
        print(f"Error getting sorted product recommendations from Gemini: {e}")


if __name__ == "__main__":
    main()
