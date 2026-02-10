from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.db.base import get_db
from app.core.analytics import AnalyticsEngine

router = APIRouter()

@router.get("", response_model=List[schemas.reports.TaskReport])
def get_reports(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    return db.query(models.task_tracking.TaskReport).filter(
        models.task_tracking.TaskReport.org_id == org_id
    ).all()

@router.post("/generate", response_model=schemas.reports.TaskReport)
def generate_report(
    report_type: str, # Daily, Weekly, Monthly
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    # Logic to trigger analytics engine and save report
    # For now, stub data based on current tasks
    tasks = db.query(models.task_tracking.Task).filter(
        models.task_tracking.Task.org_id == org_id,
        models.task_tracking.Task.assignee_id == current_user.id
    ).all()
    
    total = len(tasks)
    completed = len([t for t in tasks if t.status == "Completed"])
    pending = total - completed
    efficiency = (completed / total * 100) if total > 0 else 0
    
    rating = 1
    if efficiency > 90: rating = 5
    elif efficiency > 75: rating = 4
    elif efficiency > 50: rating = 3
    elif efficiency > 25: rating = 2
    
    db_obj = models.task_tracking.TaskReport(
        org_id=org_id,
        user_id=current_user.id,
        report_type=report_type,
        total_tasks=total,
        completed_tasks=completed,
        pending_tasks=pending,
        efficiency_score=efficiency,
        rating=rating,
        start_date=None, # TBD
        end_date=None # TBD
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
