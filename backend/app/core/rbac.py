from sqlalchemy.orm import Session
from app.models.core import User, Role, Permission
import json

class RBACService:
    @staticmethod
    def get_role_permissions(db: Session, role_id: int):
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return set()
        
        permissions = {p.code for p in role.permissions}
        
        # Handle granular overrides from JSON
        if role.permissions_json:
            try:
                overrides = json.loads(role.permissions_json)
                # overrides structure: {"code": true/false}
                for code, val in overrides.items():
                    if val:
                        permissions.add(code)
                    elif code in permissions:
                        permissions.remove(code)
            except:
                pass

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
            
        if role.name == "Admin":
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

    @staticmethod
    def initialize_org_roles(db: Session, org_id: int):
        """
        Initialize standard roles and permissions for a new organization.
        """
        # Define Permissions (Same as init_permissions.py)
        # We assume permissions are GLOBAL and already seeded in the DB.
        # If not, we should ensure they exist. But typically permissions are system-wide, roles are per-org.
        
        # Role Mappings
        ROLE_MAPPINGS = {
            "Super Admin": [
                "task:view", "task:create", "task:edit_own", "task:edit_all", "task:assign", "task:status", "task:priority", "task:comment", "task:upload", "task:delete", "task:archive",
                "project:view", "project:create", "project:edit", "project:delete", "project:members", "project:visibility",
                "user:invite", "user:remove", "user:role_assign", "role:manage",
                "report:view", "report:own", "report:team", "report:export", "report:audit", "report:org",
                "settings:manage", "settings:workflow", "settings:tags", "settings:integrations", "settings:billing", "settings:branding", "settings:rbac"
            ],
            "Admin": [
                "task:view", "task:create", "task:edit_own", "task:edit_all", "task:assign", "task:status", "task:priority", "task:comment", "task:upload", "task:delete", "task:archive",
                "project:view", "project:create", "project:edit", "project:delete", "project:members", "project:visibility",
                "user:invite", "user:remove", "user:role_assign", "role:manage",
                "report:view", "report:own", "report:team", "report:export", "report:audit",
                "settings:manage", "settings:workflow", "settings:tags", "settings:integrations", "settings:branding"
            ],
            "HR Manager": [
                "task:view", "task:create", "task:edit_own", "task:status", "task:comment", "task:upload",
                "user:invite", "user:remove", "user:role_assign",
                "report:view", "report:own"
            ],
            "Project Manager": [
                "task:view", "task:create", "task:edit_all", "task:assign", "task:status", 
                "task:priority", "task:comment", "task:upload", "task:delete", "task:archive",
                "project:view", "project:create", "project:edit", "project:members", "project:visibility",
                "report:view", "report:own", "report:team", "report:export"
            ],
            "Finance Viewer": [
                "task:view", "project:view", "report:view", "report:org"
            ],
            "Contributor": [
                "task:view", "task:create", "task:edit_own", "task:status", "task:comment", "task:upload",
                "project:view",
                "report:view", "report:own"
            ],
            "Guest": [
                "task:view", "project:view"
            ]
        }

        # Cache permissions to avoid repeated queries
        all_perms = db.query(Permission).all()
        perm_map = {p.code: p for p in all_perms}

        for role_name, codes in ROLE_MAPPINGS.items():
            # Check if role exists for this org
            role = db.query(Role).filter(Role.org_id == org_id, Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, org_id=org_id, is_standard=True)
                db.add(role)
                db.flush() # Populate ID
            
            # Assign permissions
            current_perms = set(role.permissions)
            target_perms = set([perm_map[c] for c in codes if c in perm_map])
            
            # Add missing
            for p in target_perms:
                if p not in current_perms:
                    role.permissions.append(p)
            
            # For strict sync, we could remove extras, but let's just add for now to be safe
            # role.permissions = list(target_perms)
            
        db.commit()

    @staticmethod
    def setup_standard_hierarchy(db: Session, org_id: int):
        """
        Create default Branch and Department for a new organization.
        """
        from app.models.core import Branch, Department
        
        # Check if already exists
        if db.query(Branch).filter(Branch.org_id == org_id).first():
            return None
            
        branch = Branch(
            name="Main Headquarters",
            address="Primary Location",
            org_id=org_id
        )
        db.add(branch)
        db.flush()
        
        dept = Department(
            name="Operations",
            org_id=org_id,
            branch_id=branch.id
        )
        db.add(dept)
        db.flush()
        db.commit()
        return dept
