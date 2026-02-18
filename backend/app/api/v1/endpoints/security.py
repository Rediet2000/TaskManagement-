from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.db.base import get_db

router = APIRouter()

@router.get("/logs", response_model=List[schemas.task.AuditLog])
def get_security_logs(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    # Requires Admin/Super Admin
    if current_user.role.name not in ["Admin", "Super Admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return db.query(models.task_tracking.AuditLog).filter(
        models.task_tracking.AuditLog.org_id == current_user.org_id
    ).order_by(
        models.task_tracking.AuditLog.timestamp.desc()
    ).offset(skip).limit(limit).all()

@router.post("/log")
def create_security_log(
    action: str,
    details: str,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    db_obj = models.task_tracking.AuditLog(
        user_id=current_user.id,
        org_id=current_user.org_id,
        action=action,
        details=details
    )
    db.add(db_obj)
    db.commit()
    return {"status": "success"}
@router.get("/export")
def export_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Export audit logs as a CSV file.
    """
    if current_user.role.name not in ["Admin", "Super Admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    logs = db.query(models.task_tracking.AuditLog).filter(
        models.task_tracking.AuditLog.org_id == current_user.org_id
    ).order_by(models.task_tracking.AuditLog.timestamp.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp", "User ID", "Action", "Details"])
    
    for log in logs:
        writer.writerow([
            log.id,
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            log.user_id,
            log.action,
            log.details
        ])
        
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=audit_logs_{current_user.org_id}.csv"}
    )
