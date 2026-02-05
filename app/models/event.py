import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calendar_id = Column(UUID(as_uuid=True), ForeignKey("calendars.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    is_all_day = Column(Boolean, default=False, nullable=False)
    status = Column(String, default="confirmed", nullable=False)  # confirmed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    calendar = relationship("Calendar", back_populates="events")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_events_calendar_start', 'calendar_id', 'start_at'),
        Index('ix_events_calendar_end', 'calendar_id', 'end_at'),
    )
