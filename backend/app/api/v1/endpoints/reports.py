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

@router.get("/admin-stats")
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    """
    Get high-level statistics for the Company Admin Dashboard.
    """
    # Check permissions (Admin only)
    # Ideally use deps.check_permission, but simple role check for MVP
    if current_user.role.name not in ["Admin", "Super Admin"]:
         raise HTTPException(status_code=403, detail="Not authorized")

    # 1. User Stats
    total_users = db.query(models.core.User).filter(models.core.User.org_id == org_id).count()
    active_users = db.query(models.core.User).filter(models.core.User.org_id == org_id, models.core.User.is_active == True).count()
    
    # 2. Project/Task Stats (Assuming 'Project' is represented by high-level tasks or similar, 
    # but for now we'll count total tasks as proxy for activity)
    total_tasks = db.query(models.task_tracking.Task).filter(models.task_tracking.Task.org_id == org_id).count()
    open_tasks = db.query(models.task_tracking.Task).filter(
        models.task_tracking.Task.org_id == org_id, 
        models.task_tracking.Task.status != "Done"
    ).count()
    
    # 3. Storage Usage (Mocked for now as we don't track file sizes in DB yet)
    # In future, sum(attachment.size)
    storage_used_mb = 125.5 # Mock value
    storage_limit_mb = 10240 # 10GB limit example
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "tasks": {
            "total": total_tasks,
            "open": open_tasks,
            "completed": total_tasks - open_tasks
        },
        "storage": {
            "used_mb": storage_used_mb,
            "limit_mb": storage_limit_mb,
            "percent": round((storage_used_mb / storage_limit_mb) * 100, 1)
        }
    }
