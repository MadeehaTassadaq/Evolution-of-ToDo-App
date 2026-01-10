"""
Security Configuration for Todo AI Chatbot
Contains security settings and validation checks
"""

import os
from datetime import timedelta


class SecurityConfig:
    """Security configuration settings."""

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Rate limiting (to be implemented)
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

    # Input validation limits
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))
    MAX_USERNAME_LENGTH = int(os.getenv("MAX_USERNAME_LENGTH", "100"))
    MAX_PASSWORD_LENGTH = int(os.getenv("MAX_PASSWORD_LENGTH", "128"))

    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        return True, ""

    @staticmethod
    def sanitize_input(input_str: str, max_length: int = None) -> str:
        """
        Sanitize user input to prevent injection attacks.

        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if input_str is None:
            return ""

        # Strip whitespace
        sanitized = input_str.strip()

        # Limit length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        # Remove potentially dangerous characters
        # This is a basic implementation - consider using a proper library for production
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '`', '\\']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized


# Initialize security config
security_config = SecurityConfig()


def get_token_expiry_time():
    """Get the token expiry time."""
    return timedelta(minutes=security_config.ACCESS_TOKEN_EXPIRE_MINUTES)


def is_valid_token(token: str) -> bool:
    """
    Basic token validation.

    Args:
        token: Token to validate

    Returns:
        True if token is valid, False otherwise
    """
    if not token or len(token) < 10:  # Basic length check
        return False

    # Additional validation would go here
    return True