# Vercel serverless function entry point
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the FastAPI app
from main import app

# Vercel expects either 'app' or a handler function
# For FastAPI, we can export the app directly
app = app
