from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.db.base import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.task.Task])
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

@router.post("/", response_model=schemas.task.Task)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: schemas.task.TaskCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task.
    """
    db_obj = models.task_tracking.Task(
        **task_in.dict(),
        creator_id=current_user.id,
        org_id=current_user.org_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{id}", response_model=schemas.task.Task)
def update_task(
    *,
    db: Session = Depends(get_db),
    id: int,
    task_in: schemas.task.TaskCreate,
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
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
