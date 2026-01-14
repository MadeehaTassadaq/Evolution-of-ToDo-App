#!/usr/bin/env python3
"""Debug script to check auth service configuration"""

import os
import sys
sys.path.append('.')

# Import the auth service to check what secret key it's using
from services.auth_service import AuthService, auth_service

print(f"Secret key in auth_service: '{auth_service.secret_key}'")
print(f"Environment JWT_SECRET_KEY: '{os.getenv('JWT_SECRET_KEY')}'")

# Test the token we're using
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfMTIzIiwiZXhwIjoxNzY4MzAyNTI1fQ.rodhkVgqwOb_dargQ9JJiSEuknKRq21fhLcLJOatkvQ'

verification_result = auth_service.verify_token(token)
print(f"Token verification result: {verification_result}")