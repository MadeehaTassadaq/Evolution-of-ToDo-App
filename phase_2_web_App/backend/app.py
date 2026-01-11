# Hugging Face Space entry point
# This file is used by Hugging Face Spaces to run the application
import os
from app.main import app

# Make sure the app is available at the module level
# Hugging Face Spaces will look for the 'app' variable
if __name__ == "__main__":
    # This is just for local testing
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)