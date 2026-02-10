import sys
import os
import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine, Base
from app.models.core import User, Organization, Role, AllowedDomain, MailList
from app.models.task_tracking import Task, ProblemArea, TaskReport, AuditLog, Notification
from app.core.security import get_password_hash
from app.core.config import settings

def create_superadmin():
    # 0. Wait for DB to be ready
    max_retries = 30
    retry_interval = 2
    
    print("Waiting for database to be ready...")
    for i in range(max_retries):
        try:
            # Try to connect and execute a simple query
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready!")
            break
        except OperationalError as e:
            if i == max_retries - 1:
                print(f"Error: Database not ready after {max_retries} retries. {e}")
                sys.exit(1)
            print(f"Database not ready yet... ({i+1}/{max_retries})")
            time.sleep(retry_interval)

    # Ensure tables exist
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Create Default Organization
        org = db.query(Organization).filter(Organization.name == "System").first()
        if not org:
            org = Organization(
                name="System", 
                is_active=True,
                email_domain=settings.FIRST_ALLOWED_DOMAIN
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"Created organization: {org.name} with domain: {org.email_domain}")
        else:
            # Update domain if it changed in env
            org.email_domain = settings.FIRST_ALLOWED_DOMAIN
            db.commit()
            print(f"Updated organization domain to: {org.email_domain}")
        
        # 2. Create Super Admin Role
        role = db.query(Role).filter(Role.name == "Super Admin", Role.org_id == org.id).first()
        if not role:
            role = Role(name="Super Admin", org_id=org.id)
            db.add(role)
            db.commit()
            db.refresh(role)
            print(f"Created role: {role.name}")

        # 3. Create Super Admin User
        user_email = settings.FIRST_SUPERADMIN_EMAIL
        password = settings.FIRST_SUPERADMIN_PASSWORD
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = User(
                email=user_email,
                hashed_password=get_password_hash(password),
                full_name="System Superadmin",
                org_id=org.id,
                role_id=role.id,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            print(f"Created Superadmin user: {user_email}")
        else:
            print(f"User {user_email} already exists.")
            # Update password anyway as requested
            user.hashed_password = get_password_hash(password)
            db.commit()
            print("Password updated for existing user.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_superadmin()
