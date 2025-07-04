# Eventually Yours Shopping App - Backend Entry Point
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from api.backend_api import app

if __name__ == "__main__":
    print(f"Starting {app.config.get('APP_NAME', 'Eventually Yours Shopping App')} Backend...")
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY environment variable not set!")
        print("Please create a .env file with your API key or set the environment variable.")
    
    # Use production mode by default, but allow debug mode via environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug_mode, host="0.0.0.0", port=5000) 