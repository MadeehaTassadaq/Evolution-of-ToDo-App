from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session, select
from database.session import get_session
from services.auth_service import AuthService, auth_service
from database.models.user import User, UserCreate
from passlib.context import CryptContext
import re


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    """Request model for login endpoint."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Response model for login endpoint."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class RegisterRequest(BaseModel):
    """Request model for registration endpoint."""
    username: str
    email: str
    password: str

    def validate_password(self, password: str) -> bool:
        """Validate password strength."""
        # At least 8 characters, one uppercase, one lowercase, one digit
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True


class RegisterResponse(BaseModel):
    """Response model for registration endpoint."""
    user_id: str
    username: str
    message: str


router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash for the given password."""
    return pwd_context.hash(password)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return access token.

    Args:
        request: Login credentials (username and password)
        session: Database session for database operations

    Returns:
        LoginResponse with access token and user information
    """
    # Find user by username
    statement = select(User).where(User.username == request.username)
    user = session.exec(statement).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = auth_service.create_access_token(data={"sub": user.id, "username": user.username})

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user.

    Args:
        request: Registration details (username, email, password)
        session: Database session for database operations

    Returns:
        RegisterResponse with user information
    """
    # Validate password
    if not request.validate_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and include an uppercase letter, lowercase letter, and digit"
        )

    # Check if username already exists
    statement = select(User).where(User.username == request.username)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    statement = select(User).where(User.email == request.email)
    existing_email = session.exec(statement).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(request.password)

    # Create new user
    db_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return RegisterResponse(
        user_id=db_user.id,
        username=db_user.username,
        message="User registered successfully"
    )