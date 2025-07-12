# Eventually Yours Shopping App - Deployed Backend Test Tool
import requests
import json
import time

# Configuration
BACKEND_URL = "https://eventually-yours-shopping-app-project-production.up.railway.app"
TIMEOUT = 30  # Increased timeout for Railway

def test_health_check():
    """Test the health check endpoint"""
    print("--- API Health Check ---")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Health check successful")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_session_initialization():
    """Test session initialization"""
    print("\n--- Session Initialization ---")
    session_id = f"test_session_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/init-session",
            json={"session_id": session_id},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print("✅ Session initialized successfully")
            print(f"Session ID: {session_id}")
            return session_id
        else:
            print(f"❌ Session initialization failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Session initialization error: {e}")
        return None

def test_user_info_storage(session_id):
    """Test user info storage"""
    print("\n--- User Info Storage ---")
    
    user_data = {
        "age": 22,
        "gender": "male",
        "location": "United States",
        "budgetMin": 20,
        "budgetMax": 100,
        "categories": ["electronics", "gaming", "fashion"],
        "interests": "I like technology and gaming",
        "session_id": session_id
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/user-info",
            json=user_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print("✅ User info stored successfully")
            return True
        else:
            print(f"❌ User info storage failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User info storage error: {e}")
        return False

def test_shopping_recommendations(session_id):
    """Test shopping recommendations"""
    print("\n--- Shopping Recommendations ---")
    
    shopping_data = {
        "session_id": session_id,
        "shopping_input": {
            "occasion": "Personal Use",
            "brandsPreferred": "",
            "shoppingInput": "I need gaming accessories and tech gadgets for my setup. Looking for headphones, keyboards, mice, and other gaming peripherals."
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/shopping-recommendations",
            json=shopping_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Shopping recommendations successful")
            print(f"Status: {result.get('status')}")
            print(f"Products found: {len(result.get('products', []))}")
            print(f"Processing time: {result.get('processing_time', 'N/A')}")
            print(f"Successful categories: {result.get('successful_categories', 'N/A')}")
            print(f"Total categories: {result.get('total_categories', 'N/A')}")
            
            # Display the products
            products = result.get('products', [])
            if products:
                print(f"\n📦 Found {len(products)} products:")
                for i, product in enumerate(products, 1):
                    print(f"{i}. {product.get('name', 'No name')}")
                    print(f"   Price: {product.get('price', 0)} {product.get('currency', '$')}")
                    print(f"   Category: {product.get('category', 'Unknown')}")
                    print(f"   Rating: {product.get('rating', 0)}")
                    print()
            
            return True
        else:
            print(f"❌ Shopping recommendations failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Shopping recommendations error: {e}")
        return False

def test_multiple_shopping_scenarios(session_id):
    """Test multiple shopping scenarios to see different product counts"""
    print("\n--- Multiple Shopping Scenarios Test ---")
    
    test_scenarios = [
        {
            "name": "Gaming Setup (Specific)",
            "shopping_input": "I need gaming accessories and tech gadgets for my setup. Looking for headphones, keyboards, mice, and other gaming peripherals."
        },
        {
            "name": "Tech Gadgets (Broad)",
            "shopping_input": "Show me various tech gadgets and electronics within my budget"
        },
        {
            "name": "Fashion Items",
            "shopping_input": "I'm looking for clothing and fashion items, especially t-shirts and hoodies"
        },
        {
            "name": "Generic Request",
            "shopping_input": "Suggest me something"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        
        shopping_data = {
            "session_id": session_id,
            "shopping_input": {
                "occasion": "Personal Use",
                "brandsPreferred": "",
                "shoppingInput": scenario["shopping_input"]
            }
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/shopping-recommendations",
                json=shopping_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                products = result.get('products', [])
                print(f"✅ {scenario['name']}: {len(products)} products")
                print(f"   Processing time: {result.get('processing_time', 'N/A')}")
                print(f"   Successful categories: {result.get('successful_categories', 'N/A')}")
                
                # Show first 3 products as preview
                if products:
                    print("   Preview:")
                    for j, product in enumerate(products[:3], 1):
                        print(f"   {j}. {product.get('name', 'No name')[:50]}...")
            else:
                print(f"❌ {scenario['name']}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {scenario['name']}: Error - {e}")
        
        # Wait between requests
        time.sleep(2)

def main():
    print("Deployed Backend Test Tool")
    print("This tool tests the deployed backend directly")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("\n❌ API is not responding. Please check if the deployment is working.")
        return
    
    # Test session initialization
    session_id = test_session_initialization()
    if not session_id:
        print("\n❌ Session initialization failed. Stopping tests.")
        return
    
    # Test user info storage
    if not test_user_info_storage(session_id):
        print("\n❌ User info storage failed. Stopping tests.")
        return
    
    # Test multiple shopping scenarios
    test_multiple_shopping_scenarios(session_id)
    
    # Test single shopping recommendations
    if not test_shopping_recommendations(session_id):
        print("\n❌ Shopping recommendations failed.")
        return
    
    print("\n🎉 All tests passed! Your backend is working correctly.")

if __name__ == "__main__":
    main() 