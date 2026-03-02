from pydantic import BaseModel, EmailStr
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
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
