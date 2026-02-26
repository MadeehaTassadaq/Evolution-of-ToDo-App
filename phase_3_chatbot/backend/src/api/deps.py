from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import get_current_user


security = HTTPBearer()


async def get_current_active_user(current_user: str = Depends(get_current_user)):
    """
    Get the current active user from the token in the request.

    Args:
        current_user: The current user ID extracted from the token

    Returns:
        The current user ID if valid
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user