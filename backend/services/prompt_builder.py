import requests
import os


def construct_prompt(user_input, user_location, profile_details):
    prompt = (
        "You are a helpful shopping assistant. Given the user's input below, along with their location and profile details, "
        "analyze their interests, preferences, and needs. Consider all these details carefully to identify up to 10 distinct product categories "
        "that would be most relevant and appealing for them to shop for. Respond ONLY with a bullet point list of the product categories, no introduction or explanation.\n\n"
        f'User input: "{user_input}"\n\n'
        f"User location: {user_location}\n\n"
        "User profile details:\n"
        f"Age: {profile_details.get('age', '')}\n"
        f"Gender: {profile_details.get('gender', '')}\n"
        f"Budget range: {profile_details.get('budget_range', '')}\n"
        f"Favorite product categories: {profile_details.get('favorite_product_categories', '')}\n"
        f"Interests or hobbies: {profile_details.get('interests_or_hobbies', '')}\n"
        f"Preferred shopping method: {profile_details.get('preferred_shopping_method', '')}\n"
        "Generate a list of product categories based on the above information:\n\n"
        "Keep the product categories relevant to the user's input and profile details. "
        "Make sure to include a variety of categories that reflect the user's interests and preferences. "
        "The categories should be distinct and not overlap with each other. "
        "Additionally, ensure that the categories are suitable for the user's location and budget range. "
        "Additionally, keep the categories sufficiently detailed without being too specific. "
        "Avoid using vague terms like 'clothes' or 'electronics'. "
        "IMPORTANT: If the user's input mentions specific brands (e.g., Nike, Dell, Gucci, Kindle), you MUST include those brand names explicitly in the relevant categories (e.g., 'Nike trainers', 'Gucci clothing', 'Kindle e-readers'). "
        "Also, try to identify other brands the user might like based on their interests and preferences, and include those brand names in the categories where applicable. "
        "Make sure to mention brand names clearly and explicitly in the categories when applicable. "
        "However, maintain a balance between specific brand mentions and diverse categories, so as not to overemphasize brands. "
        "Adhere to these guidelines\n\n"
    )
    return prompt


def get_gemini_categories(api_key, prompt):
    print("Constructed prompt:\n")
    print(prompt)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    data = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    response_json = response.json()
    candidates = response_json.get("candidates", [])
    if candidates and "content" in candidates[0]:
        parts = candidates[0]["content"].get("parts", [])
        if parts:
            text = parts[0].get("text", "")
            categories = [
                line.strip("0123456789. \t-")
                for line in text.splitlines()
                if line.strip()
            ]
            print("Generated categories:")
            for category in categories:
                print(category)
            return categories
    return []


def build_and_get_categories(api_key, user_input, user_location, profile_details):
    prompt = construct_prompt(user_input, user_location, profile_details)
    categories = get_gemini_categories(api_key, prompt)
    return categories


def fetch_user_profile(api_url, username=None, email=None):
    params = {}
    if username:
        params["username"] = username
    elif email:
        params["email"] = email
    else:
        raise ValueError("Must provide username or email to fetch user profile")

    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Error fetching user profile: {response.status_code} - {response.text}"
            )
            return {}
    except Exception as e:
        print(f"Exception during API call: {e}")
        return {}


if __name__ == "__main__":
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        exit(1)
        
    api_url = "https://eventually-yours-shopping-app-project-production.up.railway.app/api/user_profile/"  # Adjust to your Django API URL

    user_input = input("Enter your shopping input: ").strip()
    # user_location = input("Enter your location: ").strip()
    username = input("Enter your username (or leave blank to use email): ").strip()
    email = None
    if not username:
        email = input("Enter your email: ").strip()

    profile_details = fetch_user_profile(api_url, username=username, email=email)

    # Fix for age_range key mismatch
    if "age_range" in profile_details:
        profile_details["age"] = profile_details.pop("age_range")

    user_location = profile_details.get("user_location", "")

    categories = build_and_get_categories(
        api_key, user_input, user_location, profile_details
    )
