#!/usr/bin/env python3
"""Quick validation test for the fixed ChatKit integration."""

import requests
import json

BASE = "http://127.0.0.1:8000"

print("Testing ChatKit Integration...")
print("-" * 50)

# Test 1: Health check
try:
    r = requests.get(f"{BASE}/health")
    print(f"✅ Backend: {r.json()['status']}")
except Exception as e:
    print(f"❌ Backend error: {e}")
    exit(1)

# Test 2: Test ThreadMetadata creation
try:
    from chatkit.types import ThreadMetadata, ActiveStatus, Page
    from datetime import datetime, timezone

    thread = ThreadMetadata(
        id="test-123",
        title="Test Thread",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        status=ActiveStatus()
    )

    serialized = thread.model_dump()
    assert isinstance(serialized['status'], dict), "Status should be a dict"
    assert serialized['status']['type'] == 'active', "Status type should be 'active'"
    print(f"✅ ThreadMetadata: {thread.title}")
    print(f"✅ Serialization: {serialized['status']}")
except Exception as e:
    print(f"❌ ThreadMetadata error: {e}")
    exit(1)

# Test 3: Test Page creation
try:
    page = Page(data=[thread], has_more=False)
    serialized_page = page.model_dump()
    assert serialized_page['has_more'] == False, "has_more should be False"
    assert len(serialized_page['data']) == 1, "Should have 1 thread"
    print(f"✅ Page: has_more={serialized_page['has_more']}, data_len={len(serialized_page['data'])}")
except Exception as e:
    print(f"❌ Page error: {e}")
    exit(1)

print("-" * 50)
print("✅ ALL TESTS PASSED!")
print("\nYour ChatKit integration should work now!")
print("\nNext steps:")
print("1. Open http://localhost:3000 in your browser")
print("2. Log in or create an account")
print("3. Click the 🤖 chat button (bottom-right)")
print("4. Try: 'Add a task to buy groceries'")
