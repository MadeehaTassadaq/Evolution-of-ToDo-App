from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from database.models.user import User


# Security scheme for API
security = HTTPBearer()


class TokenData(BaseModel):
    """Token data model."""
    user_id: str
    username: Optional[str] = None


class AuthService:
    """Service class for handling authentication operations."""

    def __init__(self):
        # Use BETTER_AUTH_SECRET for compatibility with Phase 2 web app tokens
        self.secret_key = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """
        Create an access token with the given data.

        Args:
            data: Data to encode in the token
            expires_delta: Expiration time for the token

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode a token.

        Args:
            token: JWT token to verify

        Returns:
            TokenData if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Phase 2 web app tokens have user_id as separate field and email in sub
            # Phase 3 tokens have user_id in sub
            user_id: str = payload.get("user_id") or payload.get("sub")
            username: str = payload.get("username") or payload.get("sub")

            if user_id is None:
                return None

            token_data = TokenData(user_id=user_id, username=username)
            return token_data
        except jwt.PyJWTError:
            return None

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """
        Get the current user from the token in the request.

        Args:
            credentials: HTTP authorization credentials from the request

        Returns:
            User ID if valid token, raises HTTPException otherwise
        """
        token = credentials.credentials

        token_data = self.verify_token(token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_data.user_id


# Create a global instance of the auth service
auth_service = AuthService()


# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency to get the current user from the token."""
    return await auth_service.get_current_user(credentials)