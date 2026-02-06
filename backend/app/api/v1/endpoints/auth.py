from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.base import get_db

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
    
    if org.email_domain and not user_in.email.endswith(org.email_domain):
        raise HTTPException(
            status_code=400,
            detail=f"Email must belong to domain: {org.email_domain}",
        )
    
    # Create user
    db_obj = models.core.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        org_id=user_in.org_id,
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
