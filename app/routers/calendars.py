from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Calendar
from app.schemas.calendar import CalendarCreate, CalendarUpdate, CalendarResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/calendars", tags=["Calendars"])


@router.post("", response_model=CalendarResponse, status_code=status.HTTP_201_CREATED)
def create_calendar(
    calendar_data: CalendarCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar"""
    calendar = Calendar(
        user_id=current_user.id,
        name=calendar_data.name,
        timezone=calendar_data.timezone
    )
    db.add(calendar)
    db.commit()
    db.refresh(calendar)
    
    return calendar


@router.get("", response_model=List[CalendarResponse])
def list_calendars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all calendars for current user"""
    calendars = db.query(Calendar).filter(
        Calendar.user_id == current_user.id
    ).all()
    
    return calendars


@router.get("/{calendar_id}", response_model=CalendarResponse)
def get_calendar(
    calendar_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific calendar"""
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.user_id == current_user.id
    ).first()
    
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found"
        )
    
    return calendar


@router.patch("/{calendar_id}", response_model=CalendarResponse)
def update_calendar(
    calendar_id: str,
    calendar_data: CalendarUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a calendar"""
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.user_id == current_user.id
    ).first()
    
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found"
        )
    
    # Update fields
    if calendar_data.name is not None:
        calendar.name = calendar_data.name
    if calendar_data.timezone is not None:
        calendar.timezone = calendar_data.timezone
    
    db.commit()
    db.refresh(calendar)
    
    return calendar


@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(
    calendar_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a calendar"""
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.user_id == current_user.id
    ).first()
    
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found"
        )
    
    db.delete(calendar)
    db.commit()
    
    return None
