from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import uuid
from app.utils.datetime_utils import to_vn_naive


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime
    location: Optional[str] = None
    is_all_day: bool = False

    @field_validator('start_at', 'end_at')
    @classmethod
    def normalize_to_vn_base(cls, v: datetime):
        return to_vn_naive(v)
    
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

    @field_validator('start_at', 'end_at')
    @classmethod
    def normalize_optional_to_vn_base(cls, v: Optional[datetime]):
        if v is None:
            return v
        return to_vn_naive(v)


class EventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
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
