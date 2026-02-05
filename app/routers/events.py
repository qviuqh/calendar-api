from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Calendar, Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])


def check_calendar_ownership(calendar_id: str, user_id: str, db: Session) -> Calendar:
    """Verify user owns the calendar"""
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.user_id == user_id
    ).first()
    
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found or access denied"
        )
    
    return calendar


def check_conflict(
    calendar_id: str, 
    start_at: datetime, 
    end_at: datetime, 
    db: Session,
    exclude_event_id: Optional[str] = None
) -> bool:
    """Check if event conflicts with existing events"""
    query = db.query(Event).filter(
        Event.calendar_id == calendar_id,
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
    # Verify calendar ownership
    check_calendar_ownership(str(event_data.calendar_id), str(current_user.id), db)
    
    # Check for conflicts if enabled
    if check_conflicts:
        has_conflict = check_conflict(
            str(event_data.calendar_id),
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
        calendar_id=event_data.calendar_id,
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
    calendar_id: Optional[str] = Query(None),
    start_from: Optional[datetime] = Query(None, alias="from"),
    end_to: Optional[datetime] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List events with optional filtering"""
    # Build query
    query = db.query(Event).join(Calendar).filter(
        Calendar.user_id == current_user.id
    )
    
    # Apply filters
    if calendar_id:
        query = query.filter(Event.calendar_id == calendar_id)
    
    if start_from:
        query = query.filter(Event.end_at > start_from)
    
    if end_to:
        query = query.filter(Event.start_at < end_to)
    
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
    event = db.query(Event).join(Calendar).filter(
        Event.id == event_id,
        Calendar.user_id == current_user.id
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
    event = db.query(Event).join(Calendar).filter(
        Event.id == event_id,
        Calendar.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Determine new start/end times
    new_start = event_data.start_at if event_data.start_at else event.start_at
    new_end = event_data.end_at if event_data.end_at else event.end_at
    
    # Validate end > start
    if new_end <= new_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_at must be after start_at"
        )
    
    # Check for conflicts if time changed
    if check_conflicts and (event_data.start_at or event_data.end_at):
        has_conflict = check_conflict(
            str(event.calendar_id),
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
    event = db.query(Event).join(Calendar).filter(
        Event.id == event_id,
        Calendar.user_id == current_user.id
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
