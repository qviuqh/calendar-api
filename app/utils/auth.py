from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import TYPE_CHECKING

from app.database import get_db
from app.utils.security import hash_token

if TYPE_CHECKING:
    from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> "User":
    """Get the current authenticated user from stored opaque access token"""
    from app.models.user import User

    token = credentials.credentials
    user = db.query(User).filter(User.access_token_hash == hash_token(token)).first()
    if user is None or not user.access_token_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
