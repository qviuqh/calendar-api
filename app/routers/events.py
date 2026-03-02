from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.utils.auth import get_current_user
from app.utils.datetime_utils import to_vn_naive

router = APIRouter(prefix="/events", tags=["Events"])


def check_conflict(
    user_id: str,
    start_at: datetime, 
    end_at: datetime, 
    db: Session,
    exclude_event_id: Optional[str] = None
) -> bool:
    """Check if event conflicts with existing events"""
    query = db.query(Event).filter(
        Event.user_id == user_id,
        Event.status != "cancelled",
        Event.start_at < end_at,
        Event.end_at > start_at
    )
    
    # Exclude current event when updating
    if exclude_event_id:
        query = query.filter(Event.id != exclude_event_id)
    
    conflicts = query.first()
    return conflicts is not None


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    check_conflicts: bool = Query(True, description="Check for scheduling conflicts")
):
    """Create a new event"""
    # Check for conflicts if enabled
    if check_conflicts:
        has_conflict = check_conflict(
            str(current_user.id),
            event_data.start_at,
            event_data.end_at,
            db
        )
        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event conflicts with existing event"
            )
    
    # Create event
    event = Event(
        user_id=current_user.id,
        title=event_data.title,
        description=event_data.description,
        start_at=event_data.start_at,
        end_at=event_data.end_at,
        location=event_data.location,
        is_all_day=event_data.is_all_day
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.get("", response_model=List[EventResponse])
def list_events(
    start_from: Optional[datetime] = Query(None, alias="from"),
    end_to: Optional[datetime] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List events with optional filtering"""
    # Build query
    query = db.query(Event).filter(
        Event.user_id == current_user.id
    )
    
    # Apply filters
    if start_from:
        query = query.filter(Event.end_at > to_vn_naive(start_from))
    
    if end_to:
        query = query.filter(Event.start_at < to_vn_naive(end_to))
    
    # Order by start time
    events = query.order_by(Event.start_at).all()
    
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific event"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    check_conflicts: bool = Query(True, description="Check for scheduling conflicts")
):
    """Update an event"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Determine new start/end times
    new_start = event_data.start_at if event_data.start_at else to_vn_naive(event.start_at)
    new_end = event_data.end_at if event_data.end_at else to_vn_naive(event.end_at)
    
    # Validate end > start
    if new_end <= new_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_at must be after start_at"
        )
    
    # Check for conflicts if time changed
    if check_conflicts and (event_data.start_at or event_data.end_at):
        has_conflict = check_conflict(
            str(event.user_id),
            new_start,
            new_end,
            db,
            exclude_event_id=event_id
        )
        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event conflicts with existing event"
            )
    
    # Update fields
    if event_data.title is not None:
        event.title = event_data.title
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.start_at is not None:
        event.start_at = event_data.start_at
    if event_data.end_at is not None:
        event.end_at = event_data.end_at
    if event_data.location is not None:
        event.location = event_data.location
    if event_data.is_all_day is not None:
        event.is_all_day = event_data.is_all_day
    if event_data.status is not None:
        event.status = event_data.status
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    soft_delete: bool = Query(True, description="Soft delete (cancel) instead of hard delete")
):
    """Delete or cancel an event"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if soft_delete:
        # Soft delete: mark as cancelled
        event.status = "cancelled"
        db.commit()
    else:
        # Hard delete: remove from database
        db.delete(event)
        db.commit()
    
    return None
