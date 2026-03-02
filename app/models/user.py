import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.types import UUID
from app.utils.datetime_utils import vn_now


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    access_token_hash = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=vn_now, nullable=False)
    
    # Relationships
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
