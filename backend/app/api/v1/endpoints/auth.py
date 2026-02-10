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
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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
        is_verified=False, # Should be False until email verified
    )
    db.add(db_obj)
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
    return user
