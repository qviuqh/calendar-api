from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class CalendarCreate(BaseModel):
    name: str
    timezone: str = "UTC"


class CalendarUpdate(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None


class CalendarResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    timezone: str
    created_at: datetime
    
    class Config:
        from_attributes = True
