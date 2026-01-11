from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from ..database import get_session
from ..models.user import User
import bcrypt
from ..middleware.auth import get_current_user
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from uuid import UUID
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

class UserRegistration(BaseModel):
    email: str
    password: str

@router.post("/register")
def register_user(user_data: UserRegistration, session: Session = Depends(get_session)):
    try:
        # Check if user already exists
        db_user = session.query(User).filter(User.email == user_data.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Create new user with hashed password
        db_user = User(email=user_data.email, password_hash=hashed_password)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        # Return user without password for security
        return {"id": str(db_user.id), "email": db_user.email}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during registration: {str(e)}"
        )

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    try:
        # Find user by email
        user = session.query(User).filter(User.email == form_data.username).first()

        # Validate user exists and password is correct
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token with user ID and email
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user.email,
            "user_id": str(user.id),  # Include user ID in token
            "exp": datetime.now(timezone.utc) + access_token_expires
        }
        access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user.id)
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during login: {str(e)}"
        )
