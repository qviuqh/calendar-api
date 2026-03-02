import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.types import UUID
from app.utils.datetime_utils import vn_now


class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    is_all_day = Column(Boolean, default=False, nullable=False)
    status = Column(String, default="confirmed", nullable=False)  # confirmed, cancelled
    created_at = Column(DateTime, default=vn_now, nullable=False)
    updated_at = Column(DateTime, default=vn_now, onupdate=vn_now, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="events")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_events_user_start', 'user_id', 'start_at'),
        Index('ix_events_user_end', 'user_id', 'end_at'),
    )
