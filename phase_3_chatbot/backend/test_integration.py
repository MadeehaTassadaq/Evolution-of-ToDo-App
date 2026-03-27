"""
Integration Test Script for Phase II - Phase III Bridge

This script tests the connection between Phase III chatbot and Phase II API.
Run this script to verify the integration is working correctly.

Usage:
    1. Make sure Phase II backend is running on http://localhost:8000
    2. Make sure Phase III backend is running on http://localhost:7860
    3. Run this script: python test_integration.py
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def test_phase2_api_client():
    """Test the Phase2ApiClient directly."""
    print("=" * 60)
    print("Testing Phase2ApiClient")
    print("=" * 60)

    from services.phase2_api_client import Phase2ApiClient

    # Test without token (should fail with 401)
    print("\n1. Testing API connection without token (should fail)...")
    client = Phase2ApiClient()
    result = client.list_tasks()
    print(f"   Result: {result}")
    if not result.get("success"):
        print("   ✓ Correctly failed without authentication")
    else:
        print("   ✗ Expected to fail without authentication")

    # Test with fake token (should fail)
    print("\n2. Testing API connection with fake token (should fail)...")
    client = Phase2ApiClient(access_token="fake-token")
    result = client.list_tasks()
    print(f"   Result: {result}")
    if not result.get("success"):
        print("   ✓ Correctly failed with fake token")
    else:
        print("   ✗ Expected to fail with fake token")

    print("\n" + "=" * 60)
    print("Phase2ApiClient Test Complete")
    print("=" * 60)


def test_todo_tools():
    """Test the TodoTools wrapper."""
    print("\n" + "=" * 60)
    print("Testing TodoTools")
    print("=" * 60)

    from services.todo_tools import TodoTools

    print("\n1. Testing TodoTools initialization...")
    tools = TodoTools(session=None, access_token="fake-token")
    print("   ✓ TodoTools initialized successfully")

    print("\n2. Testing list_tasks (should fail with fake token)...")
    result = tools.list_tasks(user_id="test-user")
    print(f"   Result: {result}")
    if not result.get("success"):
        print("   ✓ Correctly failed with fake token")
    else:
        print("   ✗ Expected to fail with fake token")

    print("\n" + "=" * 60)
    print("TodoTools Test Complete")
    print("=" * 60)


def test_env_vars():
    """Test environment variables."""
    print("\n" + "=" * 60)
    print("Testing Environment Variables")
    print("=" * 60)

    phase2_url = os.getenv("PHASE2_API_URL")
    print(f"\nPHASE2_API_URL: {phase2_url}")

    if phase2_url:
        print("   ✓ PHASE2_API_URL is set")
    else:
        print("   ✗ PHASE2_API_URL is not set")

    better_auth_secret = os.getenv("BETTER_AUTH_SECRET")
    print(f"\nBETTER_AUTH_SECRET: {'*' * 10 if better_auth_secret else 'NOT SET'}")

    if better_auth_secret:
        print("   ✓ BETTER_AUTH_SECRET is set")
    else:
        print("   ✗ BETTER_AUTH_SECRET is not set")

    openai_key = os.getenv("OPENAI_API_KEY")
    print(f"\nOPENAI_API_KEY: {'sk-...' if openai_key else 'NOT SET'}")

    if openai_key:
        print("   ✓ OPENAI_API_KEY is set")
    else:
        print("   ✗ OPENAI_API_KEY is not set")

    print("\n" + "=" * 60)
    print("Environment Variables Test Complete")
    print("=" * 60)


def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "=" * 60)
    print("Testing Module Imports")
    print("=" * 60)

    modules = [
        ("services.phase2_api_client", "Phase2ApiClient"),
        ("services.todo_tools", "TodoTools"),
        ("services.chatkit_server", "chatkit_server"),
    ]

    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   ✓ {module_name}.{class_name}")
        except ImportError as e:
            print(f"   ✗ {module_name}.{class_name}: {e}")
        except AttributeError as e:
            print(f"   ✗ {module_name}.{class_name}: {e}")

    print("\n" + "=" * 60)
    print("Module Imports Test Complete")
    print("=" * 60)


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Phase II - Phase III Integration Test" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")

    print("\nNote: These tests verify the bridge code is working.")
    print("For end-to-end testing, you need:")
    print("  1. Phase II backend running on http://localhost:8000")
    print("  2. Phase III backend running on http://localhost:7860")
    print("  3. A valid JWT token from Phase II")

    # Run tests
    test_env_vars()
    test_imports()
    test_phase2_api_client()
    test_todo_tools()

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 20 + "All Tests Complete!" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")


if __name__ == "__main__":
    main()
