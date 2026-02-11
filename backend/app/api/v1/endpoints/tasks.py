from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
import os
import uuid
import shutil
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app import schemas, models
from app.api import deps
from app.db.base import get_db

router = APIRouter()

@router.get("", response_model=List[schemas.task.Task])
def read_tasks(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve tasks for the current organization.
    """
    return db.query(models.task_tracking.Task).filter(
        models.task_tracking.Task.org_id == current_user.org_id
    ).offset(skip).limit(limit).all()

@router.post("", response_model=schemas.task.Task)
async def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: schemas.task.TaskCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    """
    Create new task.
    """
    db_obj = models.task_tracking.Task(
        **task_in.dict(),
        org_id=org_id,
        creator_id=current_user.id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Notify assignee if exists
    if db_obj.assignee_id:
        assignee = db.query(models.core.User).filter(models.core.User.id == db_obj.assignee_id).first()
        if assignee:
            from app.core.notifications import notification_service
            message = f"New Task Assigned: {db_obj.title}"
            # await notification_service.send_telegram_notification(assignee.telegram_chat_id, message)
            # notification_service.send_email_notification(assignee.email, "New Task Assigned", message)
            
    return db_obj

@router.put("/{id}", response_model=schemas.task.Task)
def update_task(
    *,
    db: Session = Depends(get_db),
    id: int,
    task_in: schemas.task.TaskUpdate,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a task.
    """
    task = db.query(models.task_tracking.Task).filter(
        models.task_tracking.Task.id == id,
        models.task_tracking.Task.org_id == current_user.org_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.dict(exclude_unset=True)
    print(f"DEBUG: update_task {id} data: {update_data}")
    
    # Auto-set completed_at
    if "status" in update_data:
        if update_data["status"] == schemas.task.TaskStatus.COMPLETED:
            if not task.completed_at:
                from datetime import datetime
                task.completed_at = datetime.now()
        else:
            task.completed_at = None

    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.post("/{id}/comments", response_model=schemas.task.Comment)
def create_task_comment(
    *,
    db: Session = Depends(get_db),
    id: int,
    comment_in: schemas.task.CommentBase,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    task = db.query(models.task_tracking.Task).filter(
        models.task_tracking.Task.id == id,
        models.task_tracking.Task.org_id == current_user.org_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_obj = models.task_tracking.Comment(
        content=comment_in.content,
        task_id=id,
        author_id=current_user.id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{id}/comments", response_model=List[schemas.task.Comment])
def get_task_comments(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    return db.query(models.task_tracking.Comment).filter(
        models.task_tracking.Comment.task_id == id
    ).all()

@router.post("/{id}/attachments", response_model=schemas.task.Attachment)
async def upload_task_attachment(
    *,
    db: Session = Depends(get_db),
    id: int,
    file: UploadFile = File(...),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    task = db.query(models.task_tracking.Task).filter(
        models.task_tracking.Task.id == id,
        models.task_tracking.Task.org_id == current_user.org_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Simple local storage for now
    upload_dir = f"/app/static/attachments/task_{id}"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = f"{upload_dir}/{file_id}{ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_obj = models.task_tracking.Attachment(
        file_name=file.filename,
        file_path=f"static/attachments/task_{id}/{file_id}{ext}",
        file_type=file.content_type,
        file_size=0, # Could be improved by checking buffer size
        task_id=id,
        uploader_id=current_user.id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/reports/dashboard", response_model=schemas.task.TaskReportStats)
def get_reports_dashboard(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get aggregated task report and performance metrics.
    """
    # 1. Base query for org tasks
    tasks_query = db.query(models.task_tracking.Task).filter(
        models.task_tracking.Task.org_id == current_user.org_id
    )
    all_tasks = tasks_query.all()
    
    total = len(all_tasks)
    unassigned = sum(1 for t in all_tasks if not t.assignee_id)
    pending = sum(1 for t in all_tasks if t.status == schemas.task.TaskStatus.PENDING)
    completed = sum(1 for t in all_tasks if t.status == schemas.task.TaskStatus.COMPLETED)
    started = sum(1 for t in all_tasks if t.status == schemas.task.TaskStatus.STARTED)
    
    # 2. Per User Performance
    users = db.query(models.core.User).filter(models.core.User.org_id == current_user.org_id).all()
    user_stats = []
    
    for u in users:
        u_tasks = [t for t in all_tasks if t.assignee_id == u.id]
        u_completed = [t for t in u_tasks if t.status == schemas.task.TaskStatus.COMPLETED]
        u_started = [t for t in u_tasks if t.status == schemas.task.TaskStatus.STARTED]
        
        # On-Time calculation
        on_time_count = 0
        for t in u_completed:
            # If completed_at is set and <= due_date
            if t.completed_at and t.due_date:
                if t.completed_at <= t.due_date:
                    on_time_count += 1
            elif not t.due_date:
                on_time_count += 1 # No due date = on time
        
        on_time_rate = (on_time_count / len(u_completed)) * 100 if u_completed else 0.0
        
        # Avg Rating
        rated_tasks = [t.rating for t in u_completed if t.rating is not None]
        avg_rating = sum(rated_tasks) / len(rated_tasks) if rated_tasks else None
        
        user_stats.append(schemas.task.UserPerformance(
            user_id=u.id,
            user_name=u.full_name or u.email,
            tasks_assigned=len(u_tasks),
            tasks_completed=len(u_completed),
            tasks_started=len(u_started),
            avg_rating=avg_rating,
            on_time_rate=round(on_time_rate, 1)
        ))
        
    return schemas.task.TaskReportStats(
        total_tasks=total,
        unassigned=unassigned,
        pending=pending,
        completed=completed,
        started=started,
        user_performance=user_stats
    )
