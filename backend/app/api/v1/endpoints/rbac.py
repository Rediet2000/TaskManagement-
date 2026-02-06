from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.db.base import get_db

router = APIRouter()

@router.get("/permissions", response_model=List[schemas.rbac.Permission])
def read_permissions(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve permissions.
    """
    return db.query(models.core.Permission).all()

@router.post("/roles", response_model=schemas.rbac.Role)
def create_role(
    *,
    db: Session = Depends(get_db),
    role_in: schemas.rbac.RoleCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new role.
    """
    # Check if user has permission to create role in this org
    if current_user.org_id != role_in.org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = models.core.Role(
        name=role_in.name,
        org_id=role_in.org_id,
        parent_role_id=role_in.parent_role_id
    )
    
    if role_in.permission_ids:
        permissions = db.query(models.core.Permission).filter(
            models.core.Permission.id.in_(role_in.permission_ids)
        ).all()
        role.permissions = permissions
        
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@router.get("/roles", response_model=List[schemas.rbac.Role])
def read_roles(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve roles for the current organization.
    """
    return db.query(models.core.Role).filter(models.core.Role.org_id == current_user.org_id).all()
