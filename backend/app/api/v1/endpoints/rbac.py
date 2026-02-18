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
        parent_role_id=role_in.parent_role_id,
        permissions_json=role_in.permissions_json,
        is_standard=role_in.is_standard
    )
    
    if role_in.permission_ids:
        permissions = db.query(models.core.Permission).filter(
            models.core.Permission.id.in_(role_in.permission_ids)
        ).all()
        role.permissions = permissions
        
    db.add(role)
    db.commit()
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@router.put("/roles/{role_id}", response_model=schemas.rbac.Role)
def update_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    role_in: schemas.rbac.RoleUpdate,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update role.
    """
    role = db.query(models.core.Role).filter(models.core.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if current_user.org_id != role.org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = role_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "permission_ids":
            permissions = db.query(models.core.Permission).filter(
                models.core.Permission.id.in_(value)
            ).all()
            role.permissions = permissions
        else:
            setattr(role, field, value)
            
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@router.delete("/roles/{role_id}", response_model=schemas.rbac.Role)
def delete_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    current_user: models.core.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete role.
    """
    role = db.query(models.core.Role).filter(models.core.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if current_user.org_id != role.org_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if any users are using this role
    user_count = db.query(models.core.User).filter(models.core.User.role_id == role_id).count()
    if user_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete role that is assigned to users")
    
    # Check if any roles are using this as a parent
    child_roles = db.query(models.core.Role).filter(models.core.Role.parent_role_id == role_id).count()
    if child_roles > 0:
        raise HTTPException(status_code=400, detail="Cannot delete role that has child roles. Reassign child roles first.")

    db.delete(role)
    db.commit()
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
