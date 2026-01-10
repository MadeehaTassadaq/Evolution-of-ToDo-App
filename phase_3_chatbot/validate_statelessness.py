#!/usr/bin/env python3
"""
Validation script for statelessness and safety checks in the Todo AI Chatbot
"""

import asyncio
import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path

def check_database_only_persistence():
    """Check that the application only persists data in the database."""
    print("🔍 Checking database-only persistence...")

    # Look for files that shouldn't exist for a stateless app
    suspicious_patterns = [
        "session_storage",
        "local_cache",
        ".cache",
        "temp_files",
        "memory_store",
        "in_memory_db",
        "pickle",
        ".pkl",
        "shelve",
        "db\\.shelve",
        "\\.session",
        "sessions/",
        "tmp/",
        "/tmp/"
    ]

    # Walk through the codebase looking for these patterns
    for root, dirs, files in os.walk("."):
        if "node_modules" in root or ".git" in root or "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.json')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()

                        for pattern in suspicious_patterns:
                            if pattern.lower() in content:
                                print(f"⚠️  Potential non-stateless pattern found in {filepath}: {pattern}")
                except:
                    continue

    print("✅ Database-only persistence check completed")


def check_restart_safety():
    """Check that the application can safely restart without losing state."""
    print("\n🔍 Checking restart safety...")

    # Check that no critical state is stored in memory
    stateful_indicators = [
        "global ",
        "static ",
        "singleton",
        "memory_store",
        "runtime_cache",
        "volatile",
        "transient"
    ]

    for root, dirs, files in os.walk("."):
        if "node_modules" in root or ".git" in root or "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(('.py', '.js', '.ts')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()

                        for indicator in stateful_indicators:
                            if indicator.lower() in content:
                                print(f"⚠️  Potential stateful element found in {filepath}: {indicator}")
                except:
                    continue

    print("✅ Restart safety check completed")


def check_auth_token_validation():
    """Check that authentication tokens are properly validated."""
    print("\n🔍 Checking authentication token validation...")

    # Check for proper JWT validation
    backend_dir = Path("backend")
    if backend_dir.exists():
        auth_file = backend_dir / "services" / "auth_service.py"
        if auth_file.exists():
            with open(auth_file, 'r') as f:
                content = f.read()

                if "jwt.decode" in content and "verify_token" in content:
                    print("✅ JWT token validation found")
                else:
                    print("⚠️  JWT token validation not found in auth service")

        # Check API endpoints for auth dependency
        api_dir = backend_dir / "api"
        if api_dir.exists():
            for root, dirs, files in os.walk(api_dir):
                for file in files:
                    if file.endswith('.py'):
                        filepath = Path(root) / file
                        with open(filepath, 'r') as f:
                            content = f.read()

                            # Check if endpoints use authentication
                            if "@router." in content and "Depends(get_current_user)" in content:
                                print(f"✅ Authentication dependency found in {filepath.name}")

    print("✅ Authentication validation completed")


def check_input_validation():
    """Check that input validation is properly implemented."""
    print("\n🔍 Checking input validation...")

    # Look for validation patterns in models
    models_dir = Path("database") / "models"
    if models_dir.exists():
        for model_file in models_dir.glob("*.py"):
            with open(model_file, 'r') as f:
                content = f.read()

                # Check for validation fields
                if "Field(" in content and ("min_length" in content or "max_length" in content or "regex" in content):
                    print(f"✅ Input validation found in {model_file.name}")
                else:
                    print(f"⚠️  Input validation might be missing in {model_file.name}")

    # Check for validation in services
    services_dir = Path("backend") / "services"
    if services_dir.exists():
        for service_file in services_dir.glob("*.py"):
            with open(service_file, 'r') as f:
                content = f.read()

                if "validate" in content.lower() or "assert" in content.lower():
                    print(f"✅ Validation logic found in {service_file.name}")

    print("✅ Input validation check completed")


def check_security_headers():
    """Check for security headers and safe practices."""
    print("\n🔍 Checking security practices...")

    # Check for CORS configuration
    main_file = Path("backend") / "main.py"
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()

            if "CORSMiddleware" in content and "allow_origins" in content:
                print("✅ CORS configuration found")
            else:
                print("⚠️  CORS configuration not found")

    # Check for sensitive data handling
    for root, dirs, files in os.walk("."):
        if "node_modules" in root or ".git" in root:
            continue

        for file in files:
            if file.endswith(('.py', '.js')):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()

                        # Check for hardcoded secrets
                        if "secret" in content.lower() and "=" in content and ("\"" in content or "'" in content):
                            # Check if it's in an environment variable assignment
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if "os.getenv" in line or "environment" in line.lower() or "config" in line.lower():
                                    continue  # This is probably safe
                                elif "secret" in line.lower() and "=" in line and ("\"" in line or "'" in line):
                                    if "SECRET_KEY" not in line or "_KEY =" not in line:
                                        print(f"⚠️  Potential hardcoded secret found in {filepath.name}:{i+1}")

                except:
                    continue

    print("✅ Security practices check completed")


def run_tests():
    """Run any existing tests to validate functionality."""
    print("\n🔍 Running tests if available...")

    # Look for test files
    test_patterns = [
        "test_*.py",
        "*_test.py",
        "tests/**/*.py",
        "backend/tests/**/*.py"
    ]

    has_tests = False
    for pattern in test_patterns:
        test_files = list(Path(".").glob(pattern))
        if test_files:
            has_tests = True
            print(f"Found {len(test_files)} test files")
            break

    if not has_tests:
        print("No tests found, but that's OK for validation purposes")
    else:
        print("Tests found - you should run them with pytest or unittest")

    print("✅ Test check completed")


def main():
    """Run all validation checks."""
    print("🚀 Starting Statelessness & Safety Validation for Todo AI Chatbot")
    print("=" * 60)

    check_database_only_persistence()
    check_restart_safety()
    check_auth_token_validation()
    check_input_validation()
    check_security_headers()
    run_tests()

    print("\n" + "=" * 60)
    print("✅ Validation completed! Review any warnings above.")
    print("\nFor production deployment:")
    print("- Ensure all data is persisted only in the database")
    print("- Verify authentication tokens are properly validated")
    print("- Run security scanning tools")
    print("- Consider implementing rate limiting")
    print("- Add input sanitization where needed")


if __name__ == "__main__":
    main()