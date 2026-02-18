from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.base import get_db
from app.models.core import User
from app.schemas.auth import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        print(f"--- Decoding token: {token[:15]}... ---")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        print(f"--- Token data: {token_data} ---")
    except (jwt.JWTError, ValidationError) as e:
        print(f"--- JWT Validation Error: {e} ---")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        print(f"--- User not found for ID: {token_data.sub} ---")
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Multi-tenant dependency
def get_current_org_id(
    current_user: User = Depends(get_current_active_user),
) -> int:
    return current_user.org_id

# Permission Dependency Factory
def has_permission(required_code: str):
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        # 1. Super Admin Bypass (Optional, but good for safety)
        if current_user.role and current_user.role.name == "Admin":
            return current_user
            
        # 2. Check Permissions
        if not current_user.role or not current_user.role.permissions:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required: {required_code}"
            )
            
        user_perms = {p.code for p in current_user.role.permissions}
        if required_code not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required: {required_code}"
            )
            
        return current_user
    return permission_checker
