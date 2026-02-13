from datetime import timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.base import get_db
import smtplib
from email.mime.text import MIMEText
from jose import jwt

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.auth.Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(models.core.User).filter(models.core.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Get organization's session timeout
    org = db.query(models.core.Organization).filter(models.core.Organization.id == user.org_id).first()
    timeout_minutes = org.session_timeout_minutes if org else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    access_token_expires = timedelta(minutes=timeout_minutes)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=schemas.auth.User)
def create_user_signup(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.auth.UserCreate
) -> Any:
    # Check if user already exists
    user = db.query(models.core.User).filter(models.core.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    # Check organization and domain restriction
    org = db.query(models.core.Organization).filter(models.core.Organization.id == user_in.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Collect all allowed domains for this organization
    allowed_list = []
    if org.email_domain:
        allowed_list.append(org.email_domain.lower())
    
    # Get domains from AllowedDomain table
    db_allowed = db.query(models.core.AllowedDomain).filter(
        models.core.AllowedDomain.org_id == org.id,
        models.core.AllowedDomain.is_active == True
    ).all()
    for ad in db_allowed:
        allowed_list.append(ad.domain.lower())
    
    # If any restrictions are set, validate the user's email domain
    if allowed_list:
        email_domain = user_in.email.split('@')[-1].lower()
        if email_domain not in allowed_list:
            raise HTTPException(
                status_code=400,
                detail=f"Email must belong to one of the allowed domains: {', '.join(allowed_list)}",
            )
    
    # Create user
    db_obj = models.core.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        org_id=user_in.org_id,
        role_id=user_in.role_id,
        is_active=True,
        is_verified=True, # Auto-verify if they signed up via invitation
    )
    db.add(db_obj)
    
    # Mark invitation as used
    if user_in.invitation_token:
        invitation = db.query(models.core.Invitation).filter(models.core.Invitation.token == user_in.invitation_token).first()
        if invitation:
            invitation.is_used = True
            db.add(invitation)
            
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/test-token", response_model=schemas.auth.User)
def test_token(current_user: models.core.User = Depends(deps.get_current_user)) -> Any:
    return current_user
@router.get("/me", response_model=schemas.auth.UserOut)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    u_out = schemas.auth.UserOut.from_orm(current_user)
    if current_user.role_id:
        role = db.query(models.core.Role).get(current_user.role_id)
        u_out.role_name = role.name if role else None
        if role and role.permissions:
            try:
                u_out.permissions = [p.code for p in role.permissions]
            except Exception as e:
                print(f"Error fetching permissions: {e}")
                u_out.permissions = []
    if current_user.dept_id:
        dept = db.query(models.core.Department).get(current_user.dept_id)
        u_out.dept_name = dept.name if dept else None
    if current_user.team_id:
        team = db.query(models.core.Team).get(current_user.team_id)
        u_out.team_name = team.name if team else None
    return u_out

@router.post("/password-reset-request")
def password_reset_request(
    *,
    db: Session = Depends(get_db),
    reset_in: schemas.auth.PasswordResetRequest
) -> Any:
    user = db.query(models.core.User).filter(models.core.User.email == reset_in.email).first()
    if not user:
        # Return success even if user not found to prevent email enumeration
        return {"message": "If this email is registered, you will receive a reset link shortly."}
    
    org = db.query(models.core.Organization).filter(models.core.Organization.id == user.org_id).first()
    if not org or not org.smtp_host:
        raise HTTPException(status_code=400, detail="System email not configured for this organization")
    
    token = security.create_password_reset_token(user.email)
    
    # Send email
    try:
        if org.smtp_port == 465:
            server = smtplib.SMTP_SSL(org.smtp_host, org.smtp_port, timeout=15)
        else:
            server = smtplib.SMTP(org.smtp_host, org.smtp_port, timeout=15)
            
        with server:
            if org.smtp_port != 465:
                server.starttls()
            
            if org.smtp_user and org.smtp_password:
                server.login(org.smtp_user, org.smtp_password)
            
            reset_url = f"http://localhost:4200/reset-password?token={token}"
            msg = MIMEText(f"Hello {user.full_name},\n\nYou requested a password reset. Click the link below to set a new password:\n\n{reset_url}\n\nThis link will expire in 1 hour.")
            msg['Subject'] = 'Password Reset Request'
            msg['From'] = org.smtp_from_email
            msg['To'] = user.email
            
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send reset email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send reset email")
        
    return {"message": "If this email is registered, you will receive a reset link shortly."}

@router.post("/password-reset-confirm")
def password_reset_confirm(
    *,
    db: Session = Depends(get_db),
    confirm_in: schemas.auth.PasswordResetConfirm
) -> Any:
    try:
        payload = jwt.decode(confirm_in.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("purpose") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token purpose")
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(models.core.User).filter(models.core.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = security.get_password_hash(confirm_in.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.get("/users", response_model=List[schemas.auth.UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    # Get users for the current organization
    users = db.query(models.core.User).filter(models.core.User.org_id == current_user.org_id).all()
    
    # Enrich with role and department names
    results = []
    for user in users:
        u_out = schemas.auth.UserOut.from_orm(user)
        if user.role_id:
            role = db.query(models.core.Role).get(user.role_id)
            u_out.role_name = role.name if role else None
        if user.dept_id:
            dept = db.query(models.core.Department).get(user.dept_id)
            u_out.dept_name = dept.name if dept else None
        if user.team_id:
            team = db.query(models.core.Team).get(user.team_id)
            u_out.team_name = team.name if team else None
        results.append(u_out)
        
    return results

@router.post("/users/{user_id}/toggle-status")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    user = db.query(models.core.User).filter(
        models.core.User.id == user_id,
        models.core.User.org_id == current_user.org_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
        
    user.is_active = not user.is_active
    db.commit()
    return {"status": "success", "is_active": user.is_active}

@router.put("/users/{user_id}", response_model=schemas.auth.User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.auth.UserUpdate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    user = db.query(models.core.User).filter(
        models.core.User.id == user_id,
        models.core.User.org_id == current_user.org_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        user.hashed_password = security.get_password_hash(update_data.pop("password"))
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/invite")
def invite_user(
    *,
    db: Session = Depends(get_db),
    invite_in: schemas.auth.UserInvite,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Invite a new user to the organization via a secure link.
    """
    if current_user.role.name not in ["Admin", "Super Admin", "Manager"]:
         raise HTTPException(status_code=403, detail="Not authorized to invite users")
    
    # Check if user already exists
    if db.query(models.core.User).filter(models.core.User.email == invite_in.email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    # Generate secure token
    import secrets
    import uuid
    from datetime import datetime, timedelta
    token = secrets.token_urlsafe(32)
    
    # Create Invitation Record
    invitation = models.core.Invitation(
        token=token,
        email=invite_in.email,
        org_id=current_user.org_id,
        role_id=invite_in.role_id,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()
    
    # Send Email (if configured)
    org = current_user.organization
    invite_url = f"http://localhost/signup?invitation_token={token}" # Relative to host in production, but Nginx handles it
    
    if org.smtp_host:
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            if org.smtp_port == 465:
                server = smtplib.SMTP_SSL(org.smtp_host, org.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(org.smtp_host, org.smtp_port, timeout=10)
                
            with server:
                if org.smtp_port != 465:
                    server.starttls()
                if org.smtp_user and org.smtp_password:
                    server.login(org.smtp_user, org.smtp_password)
                
                msg = MIMEText(f"Hello,\n\nYou have been invited to join {org.name} on the Task Management System.\n\nClick the link below to create your account:\n\n{invite_url}\n\nThis link will expire in 7 days.")
                msg['Subject'] = f"Invitation to join {org.name}"
                msg['From'] = org.smtp_from_email or "noreply@taskmgmt.com"
                msg['To'] = invite_in.email
                
                server.send_message(msg)
                print(f"--- EMAIL SENT TO {invite_in.email} ---")
        except Exception as e:
            print(f"Failed to send invite email: {str(e)}")
            # Fallback: link still works, admin can copy it manually if needed
            
    # For testing and manual override
    print(f"--- INVITATION LINK: {invite_url} ---")
    
    return {
        "message": f"Invitation sent to {invite_in.email}",
        "invite_link": invite_url # Return for convenience
    }

@router.get("/invitation/{token}", response_model=schemas.auth.Invitation)
def get_invitation(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Validate and retrieve invitation details.
    """
    from datetime import datetime
    inv = db.query(models.core.Invitation).filter(models.core.Invitation.token == token, models.core.Invitation.is_used == False).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found or already used")
    
    if inv.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invitation has expired")
        
    # Enrich with names
    return {
        "id": inv.id,
        "token": inv.token,
        "email": inv.email,
        "org_id": inv.org_id,
        "role_id": inv.role_id,
        "created_at": inv.created_at,
        "expires_at": inv.expires_at,
        "is_used": inv.is_used,
        "org_name": inv.organization.name,
        "role_name": inv.role.name if inv.role else None
    }

@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Suspend (deactivate) a user. Admin only.
    """
    if current_user.role.name not in ["Admin", "Super Admin"]:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    user = db.query(models.core.User).filter(
        models.core.User.id == user_id,
        models.core.User.org_id == current_user.org_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot suspend yourself")
    
    user.is_active = False # Strictly Suspend
    db.commit()
    return {"status": "success", "message": "User suspended"}

@router.post("/register-company", response_model=schemas.auth.Token)
def register_company(
    *,
    db: Session = Depends(get_db),
    reg_in: schemas.auth.CompanyRegistration
) -> Any:
    """
    Register a new company (Organization) and its first Admin user.
    """
    # 1. Check for existing email
    if db.query(models.core.User).filter(models.core.User.email == reg_in.admin_email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # 2. Check for existing organization name
    if db.query(models.core.Organization).filter(models.core.Organization.name == reg_in.org_name).first():
        raise HTTPException(status_code=400, detail="Organization name already taken")

    try:
        # 3. Create Organization
        org = models.core.Organization(
            name=reg_in.org_name,
            is_active=True,
            # Default settings
            theme_mode="system",
            system_page_title=f"{reg_in.org_name} Workspace"
        )
        db.add(org)
        db.flush() # Get org.id
        
        # 4. Initialize Roles & Permissions
        from app.core.rbac import RBACService
        RBACService.initialize_org_roles(db, org.id)
        
        # 4a. Setup Standard Hierarchy
        default_dept = RBACService.setup_standard_hierarchy(db, org.id)
        
        # 5. Get Admin Role
        admin_role = db.query(models.core.Role).filter(
            models.core.Role.org_id == org.id, 
            models.core.Role.name == "Admin"
        ).first()
        
        if not admin_role:
            raise HTTPException(status_code=500, detail="Failed to initialize roles")
            
        # 6. Create Admin User
        user = models.core.User(
            email=reg_in.admin_email,
            hashed_password=security.get_password_hash(reg_in.admin_password),
            full_name=reg_in.admin_full_name,
            is_active=True,
            is_verified=True, # Auto-verify admin? Or require email? Let's say True for MVP
            org_id=org.id,
            role_id=admin_role.id,
            dept_id=default_dept.id if default_dept else None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 7. Login (Return Token)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
