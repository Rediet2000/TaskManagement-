from sqlalchemy.orm import Session
from app.models.task_tracking import AuditLog

def create_audit_log(db: Session, user_id: int, action: str, details: str):
    """
    Utility function to create an audit log entry.
    """
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
