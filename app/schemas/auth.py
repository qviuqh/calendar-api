from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


# Auth Request/Response Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenRevoke(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None
