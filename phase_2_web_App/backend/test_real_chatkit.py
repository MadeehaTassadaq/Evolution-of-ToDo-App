#!/usr/bin/env python3
"""
Test script that simulates real ChatKit widget requests to diagnose the NoneType error.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 80)
print("REAL CHATKIT WIDGET SIMULATION TEST")
print("=" * 80)

# The real ChatKit widget sends requests with proper thread IDs
# Let's simulate the actual flow that causes the NoneType error

# Step 1: Try to create a thread (this is where the error might happen)
print("\n[TEST 1] Create new thread (like ChatKit widget does)")
print("-" * 80)

create_thread_request = {
    "type": "threads.create",
    "params": {
        "input": {
            "content": "Hello, I need to add a task",
            "metadata": {
                "source": "chatkit-widget"
            }
        }
    }
    }

print(f"Request: {json.dumps(create_thread_request, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/chatkit",
        json=create_thread_request,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"  # This will fail 401 but shows the structure
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 2: Check if the issue is with serialization
print("\n[TEST 2] Test ChatKit SDK serialization")
print("-" * 80)

try:
    from chatkit.types import ThreadMetadata, Page
    from datetime import datetime, timezone

    # Create a ThreadMetadata like the server should
    thread = ThreadMetadata(
        id="test-thread-123",
        title="Test Thread",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        status="active"
    )

    print(f"✅ ThreadMetadata created: {thread}")

    # Try to serialize it
    try:
        serialized = thread.model_dump()
        print(f"✅ Serialized ThreadMetadata: {serialized}")
    except Exception as e:
        print(f"❌ Error serializing ThreadMetadata: {e}")

    # Try to create a Page
    try:
        page = Page(data=[thread], has_more=False)
        print(f"✅ Page created")
        serialized_page = page.model_dump()
        print(f"✅ Serialized Page: {serialized_page}")
    except Exception as e:
        print(f"❌ Error with Page: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Test the actual store methods
print("\n[TEST 3] Test Store Methods")
print("-" * 80)

try:
    import asyncio
    from app.services.chatkit_store import Phase2ChatKitStore
    from chatkit.types import ThreadMetadata
    from datetime import datetime, timezone

    async def test_store():
        store = Phase2ChatKitStore()

        # Test save_thread
        test_thread = ThreadMetadata(
            id="test-thread-456",
            title="Test",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            status="active"
        )

        # Try to save (will fail without db, but should return thread)
        result = await store.save_thread(test_thread, context={})
        print(f"✅ save_thread returned: {result}")
        print(f"✅ Result type: {type(result)}")

        # Check if result can be serialized
        if hasattr(result, 'model_dump'):
            print(f"✅ Result can be serialized")
        else:
            print(f"❌ Result cannot be serialized (no model_dump method)")

    asyncio.run(test_store())

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("1. Test the actual ChatKit widget in your browser")
print("2. Check the browser console for errors")
print("3. Check the backend logs for the full error trace")
