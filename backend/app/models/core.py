from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    logo_url = Column(String, nullable=True)
    primary_color = Column(String, default="#1976d2")
    secondary_color = Column(String, default="#26c6da")
    email_domain = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # SMTP Settings
    smtp_host = Column(String, nullable=True)
    smtp_port = Column(Integer, nullable=True)
    smtp_user = Column(String, nullable=True)
    smtp_password = Column(String, nullable=True)
    smtp_from_email = Column(String, nullable=True)
    
    # Password & Session Settings
    password_min_length = Column(Integer, default=8)
    password_require_special = Column(Boolean, default=True)
    password_expiry_days = Column(Integer, default=90)
    session_timeout_minutes = Column(Integer, default=60)
    
    # LDAP Settings
    ldap_enabled = Column(Boolean, default=False)
    ldap_server = Column(String, nullable=True)
    ldap_base_dn = Column(String, nullable=True)
    
    # Notification Settings
    telegram_bot_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)
    
    # Branding Settings
    system_page_title = Column(String, default="Task Management System")
    theme_mode = Column(String, default="system") # system, light, dark
    
    # Dashboard Settings
    show_dashboard_clock = Column(Boolean, default=True)
    show_dashboard_map = Column(Boolean, default=False)
    show_dashboard_stats = Column(Boolean, default=True)
    show_dashboard_tasks = Column(Boolean, default=True)
    
    users = relationship("User", back_populates="organization")
    departments = relationship("Department", back_populates="organization")
    roles = relationship("Role", back_populates="organization")
    branches = relationship("Branch", back_populates="organization")

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String, nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="branches")
    departments = relationship("Department", back_populates="branch")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    
    organization = relationship("Organization", back_populates="departments")
    branch = relationship("Branch", back_populates="departments")
    teams = relationship("Team", back_populates="department")

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dept_id = Column(Integer, ForeignKey("departments.id"))
    org_id = Column(Integer, ForeignKey("organizations.id")) # Explicit org_id for multi-tenancy
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    department = relationship("Department", back_populates="teams")
    organization = relationship("Organization")
    members = relationship("User", back_populates="team", foreign_keys="User.team_id")
    leader = relationship("User", foreign_keys=[leader_id])

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    parent_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    
    organization = relationship("Organization", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    code = Column(String, unique=True)
    description = Column(String, nullable=True)
    
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    dept_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="users")
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])

class AllowedDomain(Base):
    __tablename__ = "allowed_domains"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", backref="allowed_domains_list")

class MailList(Base):
    __tablename__ = "mail_lists"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)
    
    organization = relationship("Organization", backref="mail_lists")
