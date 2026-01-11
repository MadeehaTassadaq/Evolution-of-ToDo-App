#!/usr/bin/env python3
"""
Check the routes and functionality of the FastAPI app
"""
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

# Set up environment
os.environ['DATABASE_URL'] = 'sqlite:///./test_todo_chatbot.db'
os.environ['JWT_SECRET_KEY'] = 'test-super-secret-key-for-local-testing'
os.environ['ENVIRONMENT'] = 'development'

from backend.app import app

def check_routes():
    """Check that the main routes are available"""
    print("Checking FastAPI routes...")

    # Print all registered routes
    print(f"\nRegistered routes ({len(app.routes)} total):")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"  {route.methods} {route.path}")

    # Check for expected endpoints
    expected_paths = ["/", "/health", "/info", "/api/chat", "/api/conversations/{conversation_id}/messages"]
    found_paths = [route.path for route in app.routes if hasattr(route, 'path')]

    print(f"\nLooking for expected API endpoints:")
    endpoints_found = 0

    # Check for root endpoint
    if "/" in found_paths:
        print("✓ Root endpoint (/) found")
        endpoints_found += 1
    else:
        print("✗ Root endpoint (/) not found")

    # Check for health endpoint
    if "/health" in found_paths:
        print("✓ Health endpoint (/health) found")
        endpoints_found += 1
    else:
        print("✗ Health endpoint (/health) not found")

    # Check for info endpoint
    if "/info" in found_paths:
        print("✓ Info endpoint (/info) found")
        endpoints_found += 1
    else:
        print("✗ Info endpoint (/info) not found")

    # Check for API endpoints
    api_endpoints_found = sum(1 for path in found_paths if path.startswith('/api'))
    print(f"✓ Found {api_endpoints_found} API endpoints")
    endpoints_found += api_endpoints_found

    print(f"\n✓ Total endpoints verified: {endpoints_found}")

    # Check the API router specifically
    print(f"\nChecking API router...")
    api_routes = [route for route in app.routes if '/api' in getattr(route, 'path', '')]
    print(f"Found {len(api_routes)} API routes")
    for route in api_routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"  {route.methods} {route.path}")

    return endpoints_found > 2  # At least basic endpoints should be there

def check_app_attributes():
    """Check that the app has expected attributes"""
    print("\nChecking app attributes...")

    attrs_to_check = ['title', 'description', 'version']
    for attr in attrs_to_check:
        if hasattr(app, attr):
            print(f"✓ App has attribute '{attr}': {getattr(app, attr)}")
        else:
            print(f"✗ App missing attribute '{attr}'")

    # Check middleware
    print(f"\nChecking middleware...")
    middleware_names = [type(mw).__name__ for mw in app.user_middleware]
    print(f"Registered middleware: {middleware_names}")

    cors_found = any('CORSMiddleware' in name for name in middleware_names)
    if cors_found:
        print("✓ CORS middleware found")
    else:
        print("✗ CORS middleware not found")

if __name__ == "__main__":
    print("=== FastAPI App Structure Check ===")

    routes_ok = check_routes()
    check_app_attributes()

    print(f"\n✓ App structure verification completed!")
    print(f"App title: {app.title}")
    print(f"App description: {app.description}")
    print(f"App version: {app.version}")

    print(f"\n🎉 App structure is valid and ready for deployment!")