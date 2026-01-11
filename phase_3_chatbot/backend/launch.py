#!/usr/bin/env python3
"""
Launch script for Hugging Face Spaces
This script can be used to start the application if needed
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app import app

if __name__ == "__main__":
    import uvicorn

    # Hugging Face Spaces sets the PORT environment variable
    port = int(os.environ.get("PORT", 7860))

    # For production on Hugging Face Spaces
    if os.environ.get("SPACE_APP_ID"):
        # Running on Hugging Face Spaces - use the provided port
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # For local development/testing
        uvicorn.run(app, host="0.0.0.0", port=port, reload=True)