import sys
import os
import logging

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.core import Permission, Role, Organization, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Permissions
PERMISSIONS = [
    # Task Management
    {"code": "task:view", "name": "View Tasks", "description": "View tasks in lists and boards"},
    {"code": "task:create", "name": "Create Tasks", "description": "Create new tasks"},
    {"code": "task:edit_own", "name": "Edit Own Tasks", "description": "Edit tasks assigned to self"},
    {"code": "task:edit_all", "name": "Edit All Tasks", "description": "Edit any task in the organization"},
    {"code": "task:assign", "name": "Assign Tasks", "description": "Assign or reassign tasks to users"},
    {"code": "task:status", "name": "Change Status", "description": "Update task status"},
    {"code": "task:priority", "name": "Set Priority/Due Date", "description": "Change task priority and due dates"},
    {"code": "task:comment", "name": "Add Comments", "description": "Post comments on tasks"},
    {"code": "task:upload", "name": "Manage Attachments", "description": "Upload and remove file attachments"},
    {"code": "task:delete", "name": "Delete Tasks", "description": "Permanently delete tasks"},
    {"code": "task:archive", "name": "Archive/Restore", "description": "Archive or restore tasks"},
    
    # Project/Workspace
    {"code": "project:view", "name": "View Projects", "description": "View project details and lists"},
    {"code": "project:create", "name": "Create Projects", "description": "Create new projects"},
    {"code": "project:edit", "name": "Edit Project Details", "description": "Update project settings and details"},
    {"code": "project:delete", "name": "Archive/Delete Projects", "description": "Archive or delete projects"},
    {"code": "project:members", "name": "Manage Members", "description": "Add or remove members from projects"},
    {"code": "project:visibility", "name": "Set Visibility", "description": "Change project visibility (Public/Private)"},
    
    # User & Role Management
    {"code": "user:invite", "name": "Invite Users", "description": "Invite new users to the organization"},
    {"code": "user:remove", "name": "Remove Users", "description": "Deactivate or remove users"},
    {"code": "user:role_assign", "name": "Assign Roles", "description": "Change user roles"},
    {"code": "role:manage", "name": "Manage Roles", "description": "Create, edit, and delete custom roles"},
    
    # Reporting
    {"code": "report:view", "name": "View Dashboards", "description": "Access general dashboards"},
    {"code": "report:own", "name": "View Personal Reports", "description": "View own performance reports"},
    {"code": "report:team", "name": "View Team Reports", "description": "View team/organization performance reports"},
    {"code": "report:export", "name": "Export Data", "description": "Export data to CSV/PDF"},
    {"code": "report:audit", "name": "View Audit Logs", "description": "Access system activity logs"},
    
    # System Settings
    {"code": "settings:manage", "name": "Manage Settings", "description": "Configure system-wide settings"},
    {"code": "settings:workflow", "name": "Configure Workflows", "description": "Setup automation and workflows"},
    {"code": "settings:tags", "name": "Manage Tags", "description": "Create and edit system tags"},
    {"code": "settings:integrations", "name": "Manage Integrations", "description": "Configure external integrations"},
    {"code": "settings:billing", "name": "View Billing", "description": "Access billing and subscription info"},
]

# Define Role Mappings (Code List)
ROLE_MAPPINGS = {
    "Admin": [p["code"] for p in PERMISSIONS], # All permissions
    "Manager": [
        "task:view", "task:create", "task:edit_all", "task:assign", "task:status", 
        "task:priority", "task:comment", "task:upload", "task:delete", "task:archive",
        "project:view", "project:create", "project:edit", "project:members", "project:visibility",
        "user:invite", "user:role_assign",
        "report:view", "report:own", "report:team", "report:export",
        "settings:workflow", "settings:tags"
    ],
    "Contributor": [
        "task:view", "task:create", "task:edit_own", "task:status", "task:comment", "task:upload",
        "project:view",
        "report:view", "report:own"
    ],
    "Viewer": [
        "task:view", "project:view", "report:view"
    ]
}

def init_permissions():
    db = SessionLocal()
    try:
        # 1. Sync Permissions
        logger.info("Syncing Permissions...")
        validation_map = {} # code -> Permission obj
        
        for perm_data in PERMISSIONS:
            perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
            if not perm:
                perm = Permission(
                    code=perm_data["code"], 
                    name=perm_data["name"], 
                    description=perm_data["description"]
                )
                db.add(perm)
                logger.info(f"Created permission: {perm.name}")
            else:
                # Update details if needed
                perm.name = perm_data["name"]
                perm.description = perm_data["description"]
            
            db.flush() # Populate ID
            validation_map[perm.code] = perm
            
        db.commit()
        
        # 2. Sync Roles
        logger.info("Syncing Roles...")
        # We need to do this for EACH organization.
        # Ideally, roles are per-org. But "System Roles" might be global prototypes?
        # The current model says Role has org_id.
        # So we should iterate all organizations and ensure these roles exist.
        
        orgs = db.query(Organization).all()
        for org in orgs:
            logger.info(f"Processing Organization: {org.name} ({org.id})")
            
            for role_name, codes in ROLE_MAPPINGS.items():
                role = db.query(Role).filter(Role.org_id == org.id, Role.name == role_name).first()
                if not role:
                    role = Role(name=role_name, org_id=org.id)
                    db.add(role)
                    logger.info(f"Created role {role_name} for org {org.name}")
                    db.flush()
                
                # Assign permissions
                current_perms = set(role.permissions)
                target_perms = set([validation_map[c] for c in codes if c in validation_map])
                
                # Add missing
                for p in target_perms:
                    if p not in current_perms:
                        role.permissions.append(p)
                
                # Remove extra? (Optional, maybe user added some manually? Let's keep manual ones for now, or reset?)
                # For strict sync: role.permissions = list(target_perms)
                # Let's do strict sync for standard roles to ensure compliance
                role.permissions = list(target_perms)
                
        db.commit()
        logger.info("Permissions initialization completed successfully.")
        
    except Exception as e:
        logger.error(f"Error initializing permissions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_permissions()
