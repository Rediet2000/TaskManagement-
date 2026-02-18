from typing import List, Optional
from pydantic import BaseModel

class PermissionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    parent_role_id: Optional[int] = None
    permissions_json: Optional[str] = None
    is_standard: bool = False

class RoleCreate(RoleBase):
    org_id: int
    permission_ids: List[int] = []

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    parent_role_id: Optional[int] = None
    permission_ids: Optional[List[int]] = None
    permissions_json: Optional[str] = None
    is_standard: Optional[bool] = None

class Role(RoleBase):
    id: int
    org_id: int
    permissions: List[Permission] = []
    
    class Config:
        from_attributes = True
