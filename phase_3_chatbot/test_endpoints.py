#!/usr/bin/env python3
"""
Test script to check the FastAPI endpoints
"""
import sys
import os
import threading
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
import warnings

# Suppress SSL warnings for local testing
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

sys.path.insert(0, os.path.abspath('.'))

# Set up environment
os.environ['DATABASE_URL'] = 'sqlite:///./test_todo_chatbot.db'
os.environ['JWT_SECRET_KEY'] = 'test-super-secret-key-for-local-testing'
os.environ['ENVIRONMENT'] = 'development'

def run_server():
    """Function to run the server in a thread for testing"""
    import uvicorn
    from backend.app import app

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def test_endpoints():
    """Test the main endpoints"""
    print("Testing FastAPI endpoints...")

    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait a moment for the server to start
    time.sleep(2)

    try:
        # Test root endpoint
        print("\nTesting root endpoint...")
        response = requests.get("http://127.0.0.1:8000/", timeout=5, verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint: {data}")
        else:
            print(f"✗ Root endpoint failed with status {response.status_code}")

        # Test health endpoint
        print("\nTesting health endpoint...")
        response = requests.get("http://127.0.0.1:8000/health", timeout=5, verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health endpoint: {data}")
        else:
            print(f"✗ Health endpoint failed with status {response.status_code}")

        # Test info endpoint
        print("\nTesting info endpoint...")
        response = requests.get("http://127.0.0.1:8000/info", timeout=5, verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Info endpoint: {data}")
        else:
            print(f"✗ Info endpoint failed with status {response.status_code}")

        print("\n✓ All endpoint tests completed successfully!")
        return True

    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure it's running on port 8000.")
        return False
    except Exception as e:
        print(f"✗ Error testing endpoints: {e}")
        return False

if __name__ == "__main__":
    success = test_endpoints()
    if success:
        print("\n🎉 All endpoint tests passed!")
    else:
        print("\n❌ Some endpoint tests failed.")
        exit(1)