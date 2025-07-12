import requests
import json
import os
from services.prompt_builder import build_and_get_categories, fetch_user_profile
from services.amazon_scraper import amazon_category_top_products, scrape_amazon_product


class SortingAlgorithm:
    def __init__(self, gemini_api_url, gemini_api_key):
        self.api_url = gemini_api_url
        self.api_key = gemini_api_key

    def build_prompt(self, user_input, user_profile_details, amazon_scraper_results):
        prompt = (
             "You are an intelligent shopping recommendation engine designed to provide diverse, comprehensive product recommendations. Based on the following data:\n\n"
    "USER'S SHOPPING REQUEST: {}\n\n"
    "USER PROFILE: {}\n\n"
    "AVAILABLE PRODUCTS FROM AMAZON: {}\n\n"
    "TASK: Analyze the user's shopping request and provide a well-rounded selection of products that maximizes customer satisfaction through variety and relevance.\n\n"
    "CORE STRATEGY:\n"
    "1. **COMPREHENSIVE COVERAGE**: If the shopping request mentions multiple items or categories, ensure you include products from ALL mentioned categories\n"
    "2. **STRATEGIC DIVERSIFICATION**: Aim for 8-12 products that cover different aspects of the request\n"
    "3. **BALANCED APPROACH**:\n"
    "   - 60% of products should directly match the shopping request\n"
    "   - 30% should address related/complementary needs\n"
    "   - 10% can be profile-based suggestions that enhance the overall shopping experience\n\n"
    "SELECTION PROCESS:\n"
    "1. **PARSE THE REQUEST**: Break down the shopping request into individual items, categories, or needs\n"
    "2. **CATEGORY MAPPING**: Group available products by relevance to each parsed element\n"
    "3. **DIVERSIFIED SELECTION**:\n"
    "   - Select 1-2 products from EACH category/item mentioned in the request\n"
    "   - Include different price points (budget, mid-range, premium) when available\n"
    "   - Vary product types, brands, and features within each category\n"
    "4. **COMPLEMENTARY ADDITIONS**: Add products that enhance or complete the shopping experience\n"
    "5. **PROFILE ENHANCEMENT**: Include 1-2 products based on user interests/profile that weren't explicitly requested but add value\n\n"
    "SELECTION CRITERIA:\n"
    "- **Primary Match**: Products directly addressing the shopping request\n"
    "- **Category Completeness**: Ensure all mentioned categories are represented\n"
    "- **Price Diversity**: Include options across different price ranges\n"
    "- **Feature Variety**: Different specifications, styles, or approaches within categories\n"
    "- **Quality Balance**: Mix of highly-rated products with good value options\n"
    "- **Profile Alignment**: Consider user's age, interests, and preferences for tie-breaking\n\n"
    "MANDATORY REQUIREMENTS:\n"
    "- NEVER select multiple products that serve identical purposes\n"
    "- NEVER focus only on the first item mentioned in the request\n"
    "- NEVER ignore latter parts of multi-item requests\n"
    "- NEVER over-concentrate on one category when multiple are mentioned\n"
    "- ALWAYS ensure variety in brands, features, and price points\n"
    "- ALWAYS verify that all aspects of the shopping request are covered\n\n"
    "OUTPUT FORMAT (for each recommended product):\n\n"
    "Product: [Product Title]\n"
    "URL: [Product URL]\n"
    "Price: [Product Price]\n"
    "Rating: [Product Rating]\n"
    "Image URL: [Image URL]\n"
    "Category Match: [Which part of the shopping request this addresses]\n"
    "Selection Type: [Direct Match/Complementary/Profile-Based]\n"
    "Reasoning: [Explain specifically how this product fits the overall shopping strategy. Mention why it was chosen over similar alternatives and highlight unique features that differentiate it from other selections.]\n\n"
    "QUALITY ASSURANCE CHECKLIST:\n"
    "Before finalizing your selection, verify:\n"
    "✓ Does this selection cover ALL aspects of the user's request?\n"
    "✓ Would a customer be satisfied with this variety and coverage?\n"
    "✓ Are there any gaps in categories or price points I should fill?\n"
    "✓ Is there sufficient diversity to avoid disappointment?\n"
    "✓ Are the products genuinely different from each other?\n"
    "✓ Do I have 8-12 products (or fewer only if genuinely limited relevant options)?\n\n"
    "FINAL INSTRUCTION: Prioritize customer delight through comprehensive, thoughtful, and diverse product selection that exceeds expectations."
        ).format(
            user_input,
            json.dumps(user_profile_details),
            json.dumps(amazon_scraper_results),
        )
        return prompt

    def get_sorted_products(
        self, user_input, user_profile_details, amazon_scraper_results
    ):
        prompt = self.build_prompt(
            user_input, user_profile_details, amazon_scraper_results
        )
        api_key = self.api_key
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        # Add timeout to the API call
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            output_text = ""
            candidates = result.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    output_text = parts[0].get("text", "")
            return output_text
        else:
            raise Exception(
                f"Gemini API request failed with status code {response.status_code}: {response.text}"
            )


if __name__ == "__main__":
    gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    gemini_api_key = os.getenv('GEMINI_API_KEY')

    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        exit(1)

    user_input = input("Enter your shopping input: ").strip()
    username = input("Enter your username (or leave blank to use email): ").strip()
    email = None
    if not username:
        email = input("Enter your email: ").strip()

    user_profile_details = fetch_user_profile(
        "https://eventually-yours-shopping-app-project-production.up.railway.app/api/user_profile/", username=username, email=email
    )
    if not user_profile_details:
        print("Failed to fetch user profile details. Exiting.")
        exit(1)

    api_key = gemini_api_key
    categories = build_and_get_categories(
        api_key,
        user_input,
        user_profile_details.get("user_location", ""),
        user_profile_details,
    )

    amazon_domain = "amazon.com"
    amazon_results = []
    for category in categories[:7]:
        urls = amazon_category_top_products(
            category,
            amazon_domain,
            num_results=3,
            budget_range=user_profile_details.get("budget_range"),
        )
        for url in urls:
            product_info = scrape_amazon_product(url)
            if product_info:
                amazon_results.append(product_info)

    sorting_algo = SortingAlgorithm(gemini_api_url, gemini_api_key)
    try:
        sorted_products_text = sorting_algo.get_sorted_products(
            user_input, user_profile_details, amazon_results
        )
        print("Sorted product recommendations based on user preferences:\n")
        print(sorted_products_text)
    except Exception as e:
        print(f"Error getting sorted product recommendations from Gemini: {e}")
