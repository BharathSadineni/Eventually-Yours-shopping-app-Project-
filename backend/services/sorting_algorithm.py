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
            "You are an intelligent shopping recommendation engine. Based on the following data:\n\n"
            "USER'S SHOPPING REQUEST: {}\n\n"
            "USER PROFILE: {}\n\n"
            "AVAILABLE PRODUCTS FROM AMAZON: {}\n\n"
            "TASK: Analyze the user's specific shopping request and select the MOST RELEVANT products from the available Amazon products.\n\n"
            "INSTRUCTIONS:\n"
            "1. PRIORITIZE the user's shopping request above all else\n"
            "2. Select 6-10 products that best match what the user is looking for\n"
            "3. ONLY include products that are genuinely relevant to the shopping request\n"
            "4. If fewer than 6 products are truly relevant, select only the relevant ones\n"
            "5. Consider the user's profile (age, gender, location, interests) as secondary factors\n"
            "6. Focus on products that directly address the shopping request\n"
            "7. If the shopping request is vague, use the user's interests and categories to guide selection\n\n"
            "OUTPUT FORMAT (for each recommended product):\n\n"
            "Product: [Product Title]\n"
            "URL: [Product URL]\n"
            "Price: [Product Price]\n"
            "Rating: [Product Rating]\n"
            "Image URL: [Image URL]\n"
            "Reasoning: [Explain specifically how this product matches the user's shopping request. Be specific about features, benefits, and why it's relevant to what they're looking for. Reference the shopping request directly.]\n\n"
            "IMPORTANT:\n"
            "- Select 6-10 products maximum, but ONLY if they are relevant\n"
            "- Quality over quantity: prefer fewer relevant products over many irrelevant ones\n"
            "- If fewer than 6 products are relevant, select only the relevant ones\n"
            "- Focus on relevance to the shopping request\n"
            "- Provide specific, detailed reasoning for each selection\n"
            "- Ensure variety while maintaining relevance\n"
            "- Do not include products that don't match the shopping request well\n"
            "- If no products are relevant, return an empty list\n"
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
