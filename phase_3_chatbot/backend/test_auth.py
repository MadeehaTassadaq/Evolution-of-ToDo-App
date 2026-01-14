#!/usr/bin/env python3
"""Test script to generate a JWT token for API testing"""

from datetime import datetime, timedelta
from jose import jwt
import os
import sys
sys.path.append('.')

# Replicate the same logic from auth_service.py
secret_key = os.getenv("JWT_SECRET_KEY")
algorithm = "HS256"

def create_test_token():
    # Create a payload with a test user ID
    payload = {
        'sub': 'test_user_123',
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }

    # Encode the token
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    print(f"Generated test token: {token}")
    return token

if __name__ == "__main__":
    token = create_test_token()
