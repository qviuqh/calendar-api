import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.types import UUID


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Optional tracking
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")