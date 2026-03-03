from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv
from sqlmodel import Session, select
import os
from uuid import UUID
from typing import Optional

from ..database import get_session
from ..models.user import User

load_dotenv()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


async def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from request.
    Supports:
    1. Authorization: Bearer <token> header
    2. ?token=<token> query parameter
    """
    # Try Authorization header first
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")

    # Try query parameter
    query_token = request.query_params.get("token")
    if query_token:
        return query_token

    return None


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """
    Get current authenticated user from JWT token.

    Supports token from Authorization: Bearer <token> header.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get the user from the database based on email
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception

    # Return the user ID and other necessary information
    return {"id": user.id, "email": user.email}


async def get_current_user_from_request(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Get current authenticated user from JWT token.

    Supports token from:
    1. Authorization: Bearer <token> header (standard OAuth2)
    2. ?token=<token> query parameter (for ChatKit widget compatibility)

    This function extracts the token from the Request object directly.
    """
    auth_token = await get_token_from_request(request)

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get the user from the database based on email
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception

    # Return the user ID and other necessary information
    return {"id": user.id, "email": user.email}
