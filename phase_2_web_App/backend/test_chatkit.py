#!/usr/bin/env python3
"""Test ChatKit endpoint with proper authentication"""

import requests
import json

# Backend URL
BASE_URL = "http://127.0.0.1:8000"

# First, let's test without authentication to see what we get
print("=" * 60)
print("Test 1: threads.list (no auth)")
print("=" * 60)

response = requests.post(
    f"{BASE_URL}/api/v1/chatkit",
    json={"type": "threads.list"},
    headers={"Content-Type": "application/json"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

print("\n" + "=" * 60)
print("Test 2: threads.create (no auth)")
print("=" * 60)

response = requests.post(
    f"{BASE_URL}/api/v1/chatkit",
    json={
        "type": "threads.create",
        "params": {
            "input": {
                "content": "Hello, this is a test message",
                "metadata": {"test": "true"}
            }
        }
    },
    headers={"Content-Type": "application/json"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:1000]}")

print("\n" + "=" * 60)
print("Test 3: Check backend is alive")
print("=" * 60)

response = requests.get(f"{BASE_URL}/health")
print(f"Health: {response.json()}")

print("\nDone!")
