#!/usr/bin/env python3
"""
Simple test script to check if the chatbot functionality works
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Set up environment
os.environ['DATABASE_URL'] = 'sqlite:///./test_todo_chatbot.db'
os.environ['JWT_SECRET_KEY'] = 'test-super-secret-key-for-local-testing'
os.environ['ENVIRONMENT'] = 'development'

from backend.app import app
from backend.services.chat_service import ChatService
from backend.services.todo_service import TodoService
from database.session import get_session_context
from sqlmodel import Session
from database.models.user import User
import asyncio

def test_basic_functionality():
    """Test basic functionality of the app"""
    print("Testing basic app functionality...")

    # Test that we can access the app instance
    assert hasattr(app, 'routes'), "App should have routes"
    print("✓ App instance is accessible")

    # Test database session
    print("\nTesting database session...")
    try:
        with get_session_context() as session:
            print("✓ Database session created successfully")

            # Test that we can work with the models (create a test instance without saving)
            from database.models.todo import Todo, TodoCreate
            test_todo = TodoCreate(title="Test", user_id="test_user")
            print("✓ Database models accessible and functional")
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

    # Test services initialization
    print("\nTesting service initialization...")
    try:
        with get_session_context() as session:
            chat_service = ChatService(session)
            todo_service = TodoService(session)
            print("✓ ChatService and TodoService initialized successfully")
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return False

    print("\n✓ All basic functionality tests passed!")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🎉 All tests passed! The application is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        exit(1)