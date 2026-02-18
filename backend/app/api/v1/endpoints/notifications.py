from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app import schemas, models
from app.api import deps

router = APIRouter()

@router.get("", response_model=List[schemas.task.NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve notifications for the current user.
    """
    return db.query(models.task_tracking.Notification).filter(
        models.task_tracking.Notification.user_id == current_user.id
    ).order_by(models.task_tracking.Notification.created_at.desc()).limit(50).all()

@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Mark a notification as read.
    """
    notification = db.query(models.task_tracking.Notification).filter(
        models.task_tracking.Notification.id == notification_id,
        models.task_tracking.Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = "Read"
    db.commit()
    return {"status": "success"}

@router.post("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Mark all notifications as read for current user.
    """
    db.query(models.task_tracking.Notification).filter(
        models.task_tracking.Notification.user_id == current_user.id,
        models.task_tracking.Notification.status == "Pending"
    ).update({"status": "Read"})
    
    db.commit()
    return {"status": "success"}
