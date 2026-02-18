from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import shutil
import os
import uuid
import json

from app import schemas, models
from app.api import deps
from app.db.base import get_db
from app.core import security
from app.models.task_tracking import Task

router = APIRouter()

@router.get("/me", response_model=schemas.auth.UserOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user's full profile"""
    u_out = schemas.auth.UserOut.from_orm(current_user)
    
    # Add role information
    if current_user.role_id:
        role = db.query(models.core.Role).get(current_user.role_id)
        u_out.role_name = role.name if role else None
        if role and role.permissions:
            try:
                u_out.permissions = [p.code for p in role.permissions]
            except Exception as e:
                print(f"Error fetching permissions: {e}")
                u_out.permissions = []
    
    # Add department and team names
    if current_user.dept_id:
        dept = db.query(models.core.Department).get(current_user.dept_id)
        u_out.dept_name = dept.name if dept else None
    if current_user.team_id:
        team = db.query(models.core.Team).get(current_user.team_id)
        u_out.team_name = team.name if team else None
    
    return u_out

@router.put("/me", response_model=schemas.auth.UserOut)
def update_profile(
    *,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    profile_in: schemas.auth.UserProfileUpdate
) -> Any:
    """Update current user's profile"""
    update_data = profile_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return get_profile(db=db, current_user=current_user)

@router.post("/photo")
def upload_profile_photo(
    *,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...)
) -> Any:
    """Upload profile photo"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed."
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "/app/static/profiles"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user's profile photo URL
    photo_url = f"/static/profiles/{unique_filename}"
    current_user.profile_photo_url = photo_url
    db.add(current_user)
    db.commit()
    
    return {"profile_photo_url": photo_url}

@router.delete("/photo")
def delete_profile_photo(
    *,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """Remove profile photo"""
    if current_user.profile_photo_url:
        # Optionally delete the file from disk
        # file_path = f"/app{current_user.profile_photo_url}"
        # if os.path.exists(file_path):
        #     os.remove(file_path)
        
        current_user.profile_photo_url = None
        db.add(current_user)
        db.commit()
    
    return {"message": "Profile photo removed"}

@router.put("/password")
def change_password(
    *,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    password_change: schemas.auth.PasswordChange
) -> Any:
    """Change user password"""
    # Verify old password
    if not security.verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )
    
    # Update password
    current_user.hashed_password = security.get_password_hash(password_change.new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.get("/activity", response_model=schemas.auth.ActivitySnapshot)
def get_activity_snapshot(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get user's activity snapshot"""
    # Count open tasks (assigned to user, not completed)
    open_tasks = db.query(func.count(Task.id))\
        .filter(
            Task.assignee_id == current_user.id,
            Task.status != 'completed'
        ).scalar() or 0
    
    # Count completed tasks
    completed_tasks = db.query(func.count(Task.id))\
        .filter(
            Task.assignee_id == current_user.id,
            Task.status == 'completed'
        ).scalar() or 0
    
    # Count overdue tasks
    today = datetime.now().date()
    overdue_tasks = db.query(func.count(Task.id))\
        .filter(
            Task.assignee_id == current_user.id,
            Task.due_date < today,
            Task.status != 'completed'
        ).scalar() or 0
    
    # Get recent tasks (last 5)
    recent_tasks = db.query(Task)\
        .filter(Task.assignee_id == current_user.id)\
        .order_by(Task.created_at.desc())\
        .limit(5)\
        .all()
    
    recent_activity = [{
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None
    } for task in recent_tasks]
    
    return {
        "open_tasks": open_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "recent_activity": recent_activity
    }

@router.put("/notifications")
def update_notification_settings(
    *,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    settings: schemas.auth.NotificationSettings
) -> Any:
    """Update notification settings"""
    if settings.email_notifications is not None:
        current_user.email_notifications = json.dumps(settings.email_notifications)
    
    if settings.in_app_notifications is not None:
        current_user.in_app_notifications = json.dumps(settings.in_app_notifications)
    
    if settings.dnd_schedule is not None:
        current_user.dnd_schedule = json.dumps(settings.dnd_schedule)
    
    db.add(current_user)
    db.commit()
    
    return {"message": "Notification settings updated"}

@router.post("/2fa/enable")
def enable_2fa(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """Enable two-factor authentication"""
    # TODO: Implement actual 2FA setup with TOTP
    current_user.two_factor_enabled = True
    db.add(current_user)
    db.commit()
    
    return {"message": "2FA enabled", "secret": "TODO: Generate TOTP secret"}

@router.post("/2fa/disable")
def disable_2fa(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """Disable two-factor authentication"""
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.add(current_user)
    db.commit()
    
    return {"message": "2FA disabled"}
