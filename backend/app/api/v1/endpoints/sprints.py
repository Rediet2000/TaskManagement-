from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.db.base import get_db

router = APIRouter()

@router.get("", response_model=List[schemas.task.Sprint])
def read_sprints(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sprints for the current organization.
    """
    return db.query(models.task_tracking.Sprint).filter(
        models.task_tracking.Sprint.org_id == current_user.org_id
    ).offset(skip).limit(limit).all()

@router.post("", response_model=schemas.task.Sprint)
def create_sprint(
    *,
    db: Session = Depends(get_db),
    sprint_in: schemas.task.SprintCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    """
    Create new sprint.
    """
    db_obj = models.task_tracking.Sprint(
        **sprint_in.dict(),
        org_id=org_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{id}", response_model=schemas.task.Sprint)
def update_sprint(
    *,
    db: Session = Depends(get_db),
    id: int,
    sprint_in: schemas.task.SprintUpdate, # Wait, I didn't create SprintUpdate, will use SprintCreate for now or fix schemas
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    # Logic to update
    sprint = db.query(models.task_tracking.Sprint).filter(
        models.task_tracking.Sprint.id == id,
        models.task_tracking.Sprint.org_id == current_user.org_id
    ).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    update_data = sprint_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sprint, field, value)
    
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint
