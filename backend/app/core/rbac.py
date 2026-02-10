from sqlalchemy.orm import Session
from app.models.core import User, Role, Permission

class RBACService:
    @staticmethod
    def get_role_permissions(db: Session, role_id: int):
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return set()
        
        permissions = {p.code for p in role.permissions}
        
        # Inherit permissions from parent role
        if role.parent_role_id:
            parent_permissions = RBACService.get_role_permissions(db, role.parent_role_id)
            permissions.update(parent_permissions)
            
        return permissions

    @staticmethod
    def has_permission(db: Session, user: User, permission_code: str) -> bool:
        if not user.role_id:
            return False
            
        user_permissions = RBACService.get_role_permissions(db, user.role_id)
        return permission_code in user_permissions

    @staticmethod
    def check_hierarchy_access(db: Session, user: User, target_org_id: int, target_dept_id: int = None, target_team_id: int = None) -> bool:
        # Super Admin access (if we define a flag or specific role)
        # For now, strict org-isolation
        if user.org_id != target_org_id:
            return False
            
        # Role-based visibility
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            return False
            
        if role.name == "Super Admin":
            return True
            
        if role.name == "Organization Admin":
            return True
            
        if role.name == "Manager":
            # Can see their own department and nested teams
            if target_dept_id and user.dept_id == target_dept_id:
                return True
            if target_team_id:
                # Check if team belongs to user's department
                # ... logic to check team -> dept relationship ...
                pass
                
        # Staff/User: Only see their own team or assigned tasks (handled in API)
        return False
