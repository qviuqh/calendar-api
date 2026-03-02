from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.auth import (
    UserRegister, UserLogin, Token, UserResponse
)
from app.utils.security import (
    hash_password, verify_password, 
    generate_access_token, hash_token
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def issue_user_access_token(user: User, db: Session) -> str:
    """Generate and persist the single active access token for a user."""
    access_token = generate_access_token()
    user.access_token_hash = hash_token(access_token)
    db.add(user)
    db.commit()
    db.refresh(user)
    return access_token


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and receive the user's long-lived access token"""
    # Verify user
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = issue_user_access_token(user, db)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/rotate-token", response_model=Token)
def rotate_access_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Replace the current user's access token with a new one."""
    access_token = issue_user_access_token(current_user, db)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invalidate the current access token (logout)."""
    current_user.access_token_hash = None
    db.add(current_user)
    db.commit()
    return None


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile (test endpoint)"""
    return current_user
