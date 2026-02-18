from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
import shutil
import os
import uuid
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from app import schemas, models
from app.api import deps
from app.db.base import get_db
import httpx

router = APIRouter()

@router.get("/organizations", response_model=List[schemas.hierarchy.Organization])
def get_organizations(
    db: Session = Depends(get_db)
) -> Any:
    return db.query(models.core.Organization).all()

@router.post("/organizations", response_model=schemas.hierarchy.Organization)
def create_organization(
    *,
    db: Session = Depends(get_db),
    org_in: schemas.hierarchy.OrganizationCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    # MVP: allow all authenticated users for now, or check for superadmin
    db_obj = models.core.Organization(**org_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Initialize roles and standard hierarchy for the new organization
    from app.core.rbac import RBACService
    RBACService.initialize_org_roles(db, db_obj.id)
    RBACService.setup_standard_hierarchy(db, db_obj.id)
    
    return db_obj

@router.get("/organizations/{org_id}", response_model=schemas.hierarchy.Organization)
def get_organization(
    org_id: int, 
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    # Basic protection: users only see their own org
    if current_user.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    org = db.query(models.core.Organization).filter(models.core.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/organizations/{org_id}", response_model=schemas.hierarchy.Organization)
def update_organization(
    *,
    db: Session = Depends(get_db),
    org_id: int,
    org_in: schemas.hierarchy.OrganizationUpdate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    if current_user.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    org = db.query(models.core.Organization).filter(models.core.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    update_data = org_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Log org update
    from app.db.utils import create_audit_log
    create_audit_log(db, current_user.id, "Update Organization", f"Updated organization profile for {org.name}", org_id)
    
    return org

@router.post("/organizations/{org_id}/logo", response_model=schemas.hierarchy.Organization)
async def upload_logo(
    *,
    db: Session = Depends(get_db),
    org_id: int,
    file: UploadFile = File(...),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Upload organization logo.
    """
    if current_user.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    org = db.query(models.core.Organization).filter(models.core.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    from app.core.config import settings
    # Define paths
    static_dir = settings.LOGOS_DIR
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(static_dir, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update logo_url in DB
    # The URL will be relative to the static mount (e.g., /static/logos/filename)
    logo_url = f"/static/logos/{filename}"
    org.logo_url = logo_url
    
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Log logo update
    from app.db.utils import create_audit_log
    create_audit_log(db, current_user.id, "Update Logo", "Uploaded new organization logo", org_id)
    
    return org

@router.get("/branches", response_model=List[schemas.hierarchy.Branch])
def get_branches(
    db: Session = Depends(get_db),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    return db.query(models.core.Branch).filter(models.core.Branch.org_id == org_id).all()

@router.post("/branches", response_model=schemas.hierarchy.Branch)
def create_branch(
    *,
    db: Session = Depends(get_db),
    branch_in: schemas.hierarchy.BranchCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    if current_user.org_id != branch_in.org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_obj = models.core.Branch(**branch_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/branches/{branch_id}", response_model=schemas.hierarchy.Branch)
def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    branch = db.query(models.core.Branch).filter(models.core.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    if current_user.org_id != branch.org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return branch

@router.put("/branches/{branch_id}", response_model=schemas.hierarchy.Branch)
def update_branch(
    *,
    db: Session = Depends(get_db),
    branch_id: int,
    branch_in: schemas.hierarchy.BranchUpdate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    branch = db.query(models.core.Branch).filter(models.core.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    if current_user.org_id != branch.org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = branch_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)
    
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch

@router.get("/departments", response_model=List[schemas.hierarchy.Department])
def get_departments(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    return db.query(models.core.Department).filter(models.core.Department.org_id == org_id).all()

@router.post("/departments", response_model=schemas.hierarchy.Department)
def create_department(
    *,
    db: Session = Depends(get_db),
    dept_in: schemas.hierarchy.DepartmentCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    # Only Org Admin or Super Admin can create
    # For now, allow all active users within their own org for MVP
    if current_user.org_id != dept_in.org_id:
         raise HTTPException(status_code=403, detail="Cannot create department for another organization")
    
    db_obj = models.core.Department(**dept_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/teams", response_model=List[schemas.hierarchy.Team])
def get_teams(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    return db.query(models.core.Team).filter(models.core.Team.org_id == org_id).all()

@router.post("/teams", response_model=schemas.hierarchy.Team)
def create_team(
    *,
    db: Session = Depends(get_db),
    team_in: schemas.hierarchy.TeamCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    if current_user.org_id != team_in.org_id:
         raise HTTPException(status_code=403, detail="Cannot create team for another organization")
    
    db_obj = models.core.Team(**team_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/allowed-domains", response_model=List[schemas.hierarchy.AllowedDomain])
def get_allowed_domains(
    db: Session = Depends(get_db),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    return db.query(models.core.AllowedDomain).filter(models.core.AllowedDomain.org_id == org_id).all()

@router.post("/allowed-domains", response_model=schemas.hierarchy.AllowedDomain)
def create_allowed_domain(
    *,
    db: Session = Depends(get_db),
    domain_in: schemas.hierarchy.AllowedDomainCreate
) -> Any:
    db_obj = models.core.AllowedDomain(**domain_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Log allowed domain addition
    from app.db.utils import create_audit_log
    create_audit_log(db, domain_in.user_id if hasattr(domain_in, "user_id") else 0, "Add Allowed Domain", f"Added domain restriction: {db_obj.domain}", db_obj.org_id)
    
    return db_obj

@router.get("/mail-lists", response_model=List[schemas.hierarchy.MailList])
def get_mail_lists(
    db: Session = Depends(get_db),
    org_id: int = Depends(deps.get_current_org_id)
) -> Any:
    return db.query(models.core.MailList).filter(models.core.MailList.org_id == org_id).all()

@router.post("/mail-lists", response_model=schemas.hierarchy.MailList)
def create_mail_list(
    *,
    db: Session = Depends(get_db),
    mail_in: schemas.hierarchy.MailListCreate
) -> Any:
    db_obj = models.core.MailList(**mail_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/test-smtp")
def test_smtp_connection(
    *,
    smtp_in: schemas.hierarchy.SMTPTest,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Test SMTP connection settings.
    """
    print(f"--- SMTP Test Start: {smtp_in.smtp_host}:{smtp_in.smtp_port} ---")
    try:
        # Create connection
        if smtp_in.use_ssl:
            print(f"Using SMTP_SSL for {smtp_in.smtp_host}:{smtp_in.smtp_port}")
            server = smtplib.SMTP_SSL(smtp_in.smtp_host, smtp_in.smtp_port, timeout=15)
        else:
            print(f"Using standard SMTP for {smtp_in.smtp_host}:{smtp_in.smtp_port}")
            server = smtplib.SMTP(smtp_in.smtp_host, smtp_in.smtp_port, timeout=15)
        
        with server:
            server.set_debuglevel(1)
            server.ehlo()
            
            if not smtp_in.use_ssl and smtp_in.use_starttls:
                print("Starting TLS")
                server.starttls()
                server.ehlo()
            
            if smtp_in.smtp_user and smtp_in.smtp_password:
                print(f"Attempting login for user: {smtp_in.smtp_user}")
                server.login(smtp_in.smtp_user, smtp_in.smtp_password)
                
            # Send a test email
            print(f"Sending test email from {smtp_in.smtp_from_email}")
            msg = MIMEText("This is a test email to verify SMTP settings in the Task Management System.")
            msg['Subject'] = 'SMTP Test Connection'
            msg['From'] = smtp_in.smtp_from_email
            msg['To'] = smtp_in.smtp_from_email # Send to self
            
            server.send_message(msg)
            print("Test email sent successfully")
        
        return {"status": "success", "message": "Connection successful and test email sent."}
    except Exception as e:
        print(f"SMTP Error encountered: {str(e)}")
        raise HTTPException(status_code=400, detail=f"SMTP Error: {str(e)}")

@router.post("/test-telegram")
async def test_telegram_connection(
    *,
    bot_token: str,
    chat_id: str,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Test Telegram bot connection and chat availability.
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "Task Management System: Operational status confirmed. Bot connection active."
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            
            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(
                    status_code=400, 
                    detail=f"Telegram API Error: {error_data.get('description', 'Unknown error')}"
                )
                
            return {"status": "success", "message": "Test message sent successfully."}
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Telegram connection failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error testing Telegram: {str(e)}")

@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """Get dashboard statistics for the current user's organization"""
    from datetime import datetime
    from sqlalchemy import func
    from app.models.task_tracking import Task, ProblemArea
    
    org_id = current_user.org_id
    
    # Total tasks
    total_tasks = db.query(func.count(Task.id))\
        .filter(Task.org_id == org_id)\
        .scalar() or 0
    
    # Active tasks (Started status)
    from app.models.task_tracking import TaskStatus
    active_tasks = db.query(func.count(Task.id))\
        .filter(
            Task.org_id == org_id,
            Task.status == TaskStatus.STARTED.value
        ).scalar() or 0
    
    # Overdue tasks (due_date < today and status != Completed)
    today = datetime.now()
    overdue_tasks = db.query(func.count(Task.id))\
        .filter(
            Task.org_id == org_id,
            Task.due_date < today,
            Task.status != TaskStatus.COMPLETED.value
        ).scalar() or 0
    
    # Total problems
    total_problems = db.query(func.count(ProblemArea.id))\
        .filter(ProblemArea.org_id == org_id)\
        .scalar() or 0
    
    return {
        "total_tasks": total_tasks,
        "active_tasks": active_tasks,
        "overdue_tasks": overdue_tasks,
        "total_problems": total_problems
    }

@router.get("/dashboard/recent-tasks")
def get_recent_tasks(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """Get recent tasks for the current user's organization"""
    from app.models.task_tracking import Task
    
    org_id = current_user.org_id
    
    tasks = db.query(Task)\
        .filter(Task.org_id == org_id)\
        .order_by(Task.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [{
        "id": task.id,
        "title": task.title,
        "priority": task.priority or "Medium",
        "status": task.status or "pending"
    } for task in tasks]
