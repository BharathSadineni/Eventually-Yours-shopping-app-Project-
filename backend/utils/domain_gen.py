import csv
import os


def load_domain_mapping(csv_filepath="amazon_domain.csv"):
    domain_mapping = {}
    if not os.path.exists(csv_filepath):
        # Create a basic domain mapping if CSV doesn't exist
        domain_mapping = {
            "united states": "www.amazon.com",
            "canada": "www.amazon.ca",
            "united kingdom": "www.amazon.co.uk",
            "germany": "www.amazon.de",
            "france": "www.amazon.fr",
            "japan": "www.amazon.co.jp",
            "australia": "www.amazon.com.au",
            "brazil": "www.amazon.com.br",
            "india": "www.amazon.in",
            "china": "www.amazon.cn",
            "mexico": "www.amazon.com.mx",
            "italy": "www.amazon.it",
            "spain": "www.amazon.es",
            "netherlands": "www.amazon.nl",
        }
        return domain_mapping
    
    with open(csv_filepath, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            domain = row["Domain"].strip()
            country = row["Country Name"].strip()
            domain_mapping[country.lower()] = domain
    return domain_mapping


_domain_mapping = load_domain_mapping()


def get_amazon_domain(user_location):
    """
    Returns the Amazon domain for the given user location (country name).
    If no exact match is found, tries partial match.
    Returns None if no match found.
    """
    user_location_lower = user_location.lower()
    # Exact match
    if user_location_lower in _domain_mapping:
        return _domain_mapping[user_location_lower]
    # Partial match
    for country, domain in _domain_mapping.items():
        if country in user_location_lower or user_location_lower in country:
            return domain
    # Return default domain if no match found
    return "www.amazon.com"
