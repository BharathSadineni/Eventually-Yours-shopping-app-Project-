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
            "You are a recommendation engine. Based on the following data:\n\n"
            "User Input: {}\n\n"
            "User Profile Details: {}\n\n"
            "Amazon Scraper Results: {}\n\n"
            "Each Amazon scraper result includes the product title, URL, price, rating, and image URL.\n\n"
            "Your task is to:\n\n"
            "Analyze the user input and profile details to infer the user's preferences, interests, budget, and needs.\n"
            "Evaluate and rank the Amazon scraper results accordingly.\n"
            "Return an ordered list of the products starting with the most relevant match.\n\n"
            "Output Format (for each recommended product):\n\n"
            "Product: [Product Title]  \n"
            "URL: [Product URL]  \n"
            "Price: [Product Price]  \n"
            "Rating: [Product Rating]  \n"
            "Image URL: [Image URL]  \n"
            "Reasoning: [Provide a detailed, varied, and specific explanation for why this product suits the user. Highlight unique features, benefits, or aspects that match the user's preferences and needs. Do not reveal the user's name or personal details; refer to the user simply as 'the user'. Avoid generic, repetitive, or vague phrases. Ensure the reasoning reflects the user's gender, location, and stated interests accurately.]\n\n"
            "Only include products in the ranked list. Ensure that your recommendations are concise, relevant, and justified."
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

        response = requests.post(url, headers=headers, json=data)
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
        "https://eventually-yours-shopping-app-backend.onrender.com/api/user_profile/", username=username, email=email
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
