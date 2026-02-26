"""
Authentication Middleware for Todo AI Chatbot
Handles JWT token verification and user context injection for MCP tools
"""

from typing import Callable, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import functools

from ..services.auth_service import verify_token


class AuthMiddleware:
    """
    Authentication middleware to verify JWT tokens and inject user context
    """

    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next: Callable):
        """
        Process the request and inject user context if authenticated
        """
        # Skip auth for health checks and public endpoints
        if request.url.path.endswith('/health'):
            response = await call_next(request)
            return response

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # For MCP tools, we might allow context injection in other ways
            # For now, set user_id to None and let individual endpoints handle auth
            request.state.user_id = None
            response = await call_next(request)
            return response

        token = auth_header[len("Bearer "):]

        # Verify the token
        user_data = verify_token(token)
        if not user_data:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"}
            )

        # Inject user_id into request state for downstream handlers
        request.state.user_id = user_data.get("user_id")

        response = await call_next(request)
        return response


def require_auth(func):
    """
    Decorator to require authentication for specific endpoints
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request') or (args[0] if args else None)

        if not hasattr(request, 'state') or not request.state.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        return await func(*args, **kwargs)

    return wrapper


def inject_user_context(tool_handler):
    """
    Decorator to inject user context into MCP tool handlers
    """
    @functools.wraps(tool_handler)
    async def wrapper(*args, **kwargs):
        # This would be used to inject the user_id into tool calls
        # The actual implementation would depend on how the MCP framework passes context
        request_context = kwargs.get('request_context', {})
        user_id = request_context.get('user_id')

        # Add user_id to kwargs if available
        if user_id:
            kwargs['user_id'] = user_id

        return await tool_handler(*args, **kwargs)

    return wrapper