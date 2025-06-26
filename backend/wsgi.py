# WSGI entry point for production deployment
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from api.backend_api import app

# For production WSGI servers like Gunicorn
if __name__ == "__main__":
    app.run() 