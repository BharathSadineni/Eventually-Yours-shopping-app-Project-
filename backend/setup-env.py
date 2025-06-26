#!/usr/bin/env python3
"""
Helper script to set up environment variables for the Eventually Yours Shopping App
"""

import os
import sys

def create_env_file():
    """Create .env file with user input"""
    
    print("🔧 Setting up environment variables for Eventually Yours Shopping App")
    print("=" * 60)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print("\n📝 Please enter your Gemini API key:")
    print("   You can get one from: https://makersuite.google.com/app/apikey")
    print("   (Your API key will be saved locally and won't be shared)")
    
    api_key = input("\nEnter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ API key cannot be empty!")
        return
    
    # Create .env file content
    env_content = f"""# API Keys
GEMINI_API_KEY={api_key}

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print("🔒 Your API key has been saved securely.")
        print("\n📋 Next steps:")
        print("   1. Make sure .env is in your .gitignore (it should be already)")
        print("   2. Start your backend with: python main.py")
        print("   3. Your app should now work with your API key!")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 