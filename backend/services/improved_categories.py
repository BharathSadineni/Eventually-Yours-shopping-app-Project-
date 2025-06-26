PRODUCT_CATEGORIES = [
    # Technology & Electronics
    "Smartphones & Accessories",
    "Laptops & Computing",
    "Gaming & Consoles",
    "Smart Home Devices",
    "Audio & Headphones",
    "Cameras & Photography",
    # Fashion & Accessories
    "Men's Fashion",
    "Women's Fashion",
    "Luxury Fashion",
    "Watches & Jewelry",
    "Bags & Accessories",
    "Athletic Wear",
    # Home & Living
    "Home Decor",
    "Furniture",
    "Kitchen & Dining",
    "Bedding & Bath",
    "Home Organization",
    "Smart Home Appliances",
    # Health & Wellness
    "Fitness Equipment",
    "Wellness Products",
    "Vitamins & Supplements",
    "Personal Care",
    "Beauty & Skincare",
    "Natural & Organic",
    # Entertainment & Media
    "Books & E-readers",
    "Video Games",
    "Movies & TV Shows",
    "Music & Instruments",
    "Board Games & Puzzles",
    "Collectibles",
    # Sports & Outdoors
    "Outdoor Gear",
    "Sports Equipment",
    "Camping & Hiking",
    "Cycling",
    "Water Sports",
    "Winter Sports",
    # Hobbies & Crafts
    "Art Supplies",
    "DIY Tools",
    "Craft Materials",
    "Photography Equipment",
    "Musical Instruments",
    # Food & Beverages
    "Gourmet Foods",
    "Coffee & Tea",
    "Wine & Spirits",
    "Specialty Foods",
    # Pet Supplies
    "Dog Supplies",
    "Cat Supplies",
    "Pet Care & Health",
]

# Shopping Input Fields
SHOPPING_INPUT_FIELDS = {
    "occasion": [
        "Personal Use",
        "Gift",
        "Special Event",
        "Home Improvement",
        "Work/Professional",
        "Collection/Hobby",
        "Travel/Adventure",
        "Fitness/Health Goal",
    ],
    "price_tiers": [
        "Budget (Under $50)",
        "Mid-Range ($50-$200)",
        "Premium ($200-$500)",
        "Luxury ($500+)",
    ],
    "preferences": {
        "brand_loyalty": [
            "Prefer Specific Brands",
            "Open to Alternatives",
            "Brand Agnostic",
        ],
        "quality_preference": [
            "Value for Money",
            "Premium Quality",
            "Luxury/High-End",
            "Budget-Friendly",
        ],
        "sustainability": [
            "Eco-Friendly",
            "Sustainable Materials",
            "Energy Efficient",
            "Not a Priority",
        ],
    },
    "use_case": [
        "Daily Use",
        "Occasional Use",
        "Professional Use",
        "Hobby/Entertainment",
        "Special Occasions",
        "Travel/Portable",
        "Home/Stationary",
    ],
}


def get_improved_prompt(user_data, shopping_input):
    """
    Constructs an improved prompt for Gemini API that focuses on user intent and preferences
    """
    prompt = f"""
You are an expert personal shopping assistant with deep knowledge of products across all categories. Your task is to analyze the following user information and provide highly relevant product recommendations.

USER PROFILE:
Age: {user_data.get('age')}
Gender: {user_data.get('gender')}
Location: {user_data.get('location')}
Interests: {user_data.get('interests')}

SHOPPING CONTEXT:
Occasion: {shopping_input.get('occasion')}
Use Case: {shopping_input.get('use_case')}
Price Range: {shopping_input.get('price_tier')}
Brand Preference: {shopping_input.get('brand_loyalty')}
Quality Preference: {shopping_input.get('quality_preference')}
Sustainability Preference: {shopping_input.get('sustainability')}

Specific Requirements: {shopping_input.get('specific_needs', '')}

TASK:
1. Analyze the user's profile and shopping context deeply.
2. Consider the following aspects:
   - Age-appropriate recommendations
   - Gender-specific preferences if applicable
   - Location-based availability and relevance
   - Price-quality balance based on preferences
   - Long-term value and usefulness
   - Brand alignment with user preferences
   - Sustainability and ethical considerations
   - Practical aspects (shipping, warranty, support)

3. Generate product recommendations that:
   - Precisely match the use case and occasion
   - Fit within the specified price range
   - Align with quality and brand preferences
   - Consider local availability and shipping
   - Account for seasonal relevance
   - Include complementary items when relevant

4. For each recommended product, provide:
   - Clear reasoning for the recommendation
   - Specific features that match user needs
   - Value proposition and benefits
   - How it fits into the user's lifestyle
   - Any relevant warnings or considerations

Format your response as a structured list of product recommendations, each with detailed reasoning that demonstrates understanding of the user's specific context and needs.
"""
    return prompt
