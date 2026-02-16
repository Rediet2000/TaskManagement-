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
    telegram_enabled = Column(Boolean, default=False)
    
    # Advanced Email Notification Settings
    email_notifications_enabled = Column(Boolean, default=True)
    emission_email_address = Column(String, nullable=True)
    bcc_recipients = Column(Boolean, default=False)
    plain_text_mail = Column(Boolean, default=False)
    address_user_in_emails_with = Column(String, default="full_name")
    emails_header = Column(String, nullable=True) # Stored as JSON string
    emails_footer = Column(String, nullable=True) # Stored as JSON string
    
    # Enhanced SMTP Settings
    email_delivery_method = Column(String, default="smtp")
    smtp_helo_domain = Column(String, nullable=True)
    smtp_authentication = Column(String, default="login")
    smtp_use_starttls = Column(Boolean, default=True)
    smtp_use_ssl = Column(Boolean, default=False)
    
    # Branding Settings
    system_page_title = Column(String, default="Task Management System")
    theme_mode = Column(String, default="system") # system, light, dark
    
    # Company Profile (Phase 15)
    industry = Column(String, nullable=True)
    address = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    default_language = Column(String, default="en")
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    
    # Dashboard Settings
    show_dashboard_clock = Column(Boolean, default=True)
    show_dashboard_map = Column(Boolean, default=False)
    show_dashboard_stats = Column(Boolean, default=True)
    show_dashboard_tasks = Column(Boolean, default=True)
    
    dashboard_layout = Column(String, default="clock,stats,tasks,map")
    dashboard_refresh_rate = Column(Integer, default=30)
    dashboard_clock_type = Column(String, default="analog")
    dashboard_metrics_config = Column(String, default="tasks,active,overdue,problems")
    dashboard_compact_mode = Column(Boolean, default=False)
    
    users = relationship("User", back_populates="organization")
    departments = relationship("Department", back_populates="organization")
    roles = relationship("Role", back_populates="organization")
    branches = relationship("Branch", back_populates="organization")
    tasks = relationship("Task", back_populates="organization")
    problem_areas = relationship("ProblemArea", back_populates="organization")

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String, nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="branches")
    departments = relationship("Department", back_populates="branch")
    problem_areas = relationship("ProblemArea", back_populates="branch")

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
    
    # Profile Information
    profile_photo_url = Column(String, nullable=True)
    username = Column(String, nullable=True, unique=True)
    job_title = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    language = Column(String, default="en")
    auth_method = Column(String, default="email_password")  # email_password, google, microsoft
    
    # Work Preferences
    task_view_preference = Column(String, default="board")  # list, board, calendar
    default_task_sort = Column(String, default="due_date")  # due_date, priority, status, created_at
    start_of_week = Column(String, default="monday")  # monday, sunday
    date_format = Column(String, default="YYYY-MM-DD")
    time_format = Column(String, default="24h")  # 12h, 24h
    
    # Notification Settings (JSON stored as string)
    email_notifications = Column(String, default='{"task_assigned":true,"status_changes":true,"mentions":true,"daily_summary":false,"weekly_summary":false}')
    in_app_notifications = Column(String, default='{"task_assigned":true,"status_changes":true,"mentions":true}')
    dnd_schedule = Column(String, nullable=True)  # JSON: {"enabled":false,"start":"22:00","end":"08:00"}
    
    # Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="users")
    department = relationship("Department")
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    role = relationship("Role")

    created_tasks = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")
    attachments = relationship("Attachment", back_populates="uploader")

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

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_used = Column(Boolean, default=False)

    organization = relationship("Organization")
    role = relationship("Role")
