from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.db.base import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.task.ProblemArea])
def read_problems(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return db.query(models.task_tracking.ProblemArea).filter(
        models.task_tracking.ProblemArea.org_id == current_user.org_id
    ).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.task.ProblemArea)
def create_problem(
    *,
    db: Session = Depends(get_db),
    problem_in: schemas.task.ProblemAreaCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    db_obj = models.task_tracking.ProblemArea(
        **problem_in.dict(),
        org_id=current_user.org_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
