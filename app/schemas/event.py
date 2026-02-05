from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import uuid


class EventCreate(BaseModel):
    calendar_id: uuid.UUID
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime
    location: Optional[str] = None
    is_all_day: bool = False
    
    @field_validator('end_at')
    @classmethod
    def end_after_start(cls, v, info):
        if 'start_at' in info.data and v <= info.data['start_at']:
            raise ValueError('end_at must be after start_at')
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location: Optional[str] = None
    is_all_day: Optional[bool] = None
    status: Optional[str] = None


class EventResponse(BaseModel):
    id: uuid.UUID
    calendar_id: uuid.UUID
    title: str
    description: Optional[str]
    start_at: datetime
    end_at: datetime
    location: Optional[str]
    is_all_day: bool
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
