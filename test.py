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
            "shoppingInput": "Suggest me something"
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
    
    # Test shopping recommendations
    if not test_shopping_recommendations(session_id):
        print("\n❌ Shopping recommendations failed.")
        return
    
    print("\n🎉 All tests passed! Your backend is working correctly.")

if __name__ == "__main__":
    main() 