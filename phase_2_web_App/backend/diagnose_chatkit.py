#!/usr/bin/env python3
"""
Comprehensive test for ChatKit integration to diagnose the NoneType error.
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

print("=" * 80)
print("CHATKIT INTEGRATION DIAGNOSTIC TEST")
print("=" * 80)

# Test 1: Health check
print("\n[TEST 1] Backend Health Check")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Test threads.list (should return Page with empty data list)
print("\n[TEST 2] threads.list (unauthenticated)")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/chatkit",
        json={"type": "threads.list"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response preview: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Test threads.create with minimal data
print("\n[TEST 3] threads.create (unauthenticated)")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/chatkit",
        json={
            "type": "threads.create",
            "params": {
                "input": {
                    "content": "Hello",
                    "metadata": {}
                }
            }
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response preview: {response.text[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Test with malformed data to see error handling
print("\n[TEST 4] Malformed request")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/chatkit",
        json={"invalid": "data"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Check OpenAI API key is set
print("\n[TEST 5] Backend Configuration")
print("-" * 80)
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    print(f"OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"DATABASE_URL: {'✅ Set' if os.getenv('DATABASE_URL') else '❌ Not set'}")
    print(f"BETTER_AUTH_SECRET: {'✅ Set' if os.getenv('BETTER_AUTH_SECRET') else '❌ Not set'}")
except Exception as e:
    print(f"❌ Error checking config: {e}")

# Test 6: Test ChatKit store directly
print("\n[TEST 6] Test ChatKit Store Directly")
print("-" * 80)
try:
    import asyncio
    from app.services.chatkit_store import Phase2ChatKitStore
    from chatkit.types import ThreadMetadata

    store = Phase2ChatKitStore()

    # Test generate_thread_id
    thread_id = store.generate_thread_id()
    print(f"✅ Generated thread_id: {thread_id}")

    # Test Page creation
    from chatkit.types import Page
    page = Page(data=[], has_more=False)
    print(f"✅ Page object created: {page}")
    print(f"✅ Page.model_dump(): {page.model_dump()}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("\nIf you're still seeing the NoneType error:")
print("1. Check the backend logs for more details")
print("2. Try opening the browser and testing the ChatKit widget")
print("3. Check the browser console (F12) for JavaScript errors")
