from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None
    org_id: Optional[int] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str
    org_id: int
    dept_id: Optional[int] = None
    team_id: Optional[int] = None
    role_id: Optional[int] = None
    invitation_token: Optional[str] = None

class UserInvite(UserBase):
    email: EmailStr
    full_name: str
    org_id: int
    role_id: Optional[int] = None

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    team_id: Optional[int] = None

class User(UserBase):
    id: int
    org_id: int
    dept_id: Optional[int] = None
    team_id: Optional[int] = None
    role_id: Optional[int] = None
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True

class UserOut(User):
    role_name: Optional[str] = None
    permissions: List[str] = []
    dept_name: Optional[str] = None
    team_name: Optional[str] = None
    
    # Profile fields
    profile_photo_url: Optional[str] = None
    username: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    auth_method: str = "email_password"
    
    # Work preferences
    task_view_preference: str = "board"
    default_task_sort: str = "due_date"
    start_of_week: str = "monday"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "24h"
    
    # Notification settings
    email_notifications: Optional[str] = None
    in_app_notifications: Optional[str] = None
    dnd_schedule: Optional[str] = None
    
    # Security
    two_factor_enabled: bool = False
    last_login: Optional[str] = None
    createdAt: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    purpose: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class OrganizationBase(BaseModel):
    name: Optional[str] = None
    email_domain: Optional[str] = None
    primary_color: Optional[str] = "#1976d2"
    secondary_color: Optional[str] = "#26c6da"
    industry: Optional[str] = None
    address: Optional[str] = None
    timezone: Optional[str] = "UTC"
    default_language: Optional[str] = "en"
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    name: str

class OrganizationUpdate(OrganizationBase):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    
    password_min_length: Optional[int] = None
    password_require_special: Optional[bool] = None
    password_expiry_days: Optional[int] = None
    session_timeout_minutes: Optional[int] = None
    
    ldap_enabled: Optional[bool] = None
    ldap_server: Optional[str] = None
    ldap_base_dn: Optional[str] = None
    
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    
    system_page_title: Optional[str] = None
    theme_mode: Optional[str] = None
    
    show_dashboard_clock: Optional[bool] = None
    show_dashboard_map: Optional[bool] = None
    show_dashboard_stats: Optional[bool] = None
    show_dashboard_tasks: Optional[bool] = None

class Organization(OrganizationBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class CompanyRegistration(BaseModel):
    org_name: str
    admin_email: EmailStr
    admin_password: str
    admin_full_name: str

# Profile-specific schemas
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    task_view_preference: Optional[str] = None
    default_task_sort: Optional[str] = None
    start_of_week: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None

class NotificationSettings(BaseModel):
    email_notifications: Optional[dict] = None
    in_app_notifications: Optional[dict] = None
    dnd_schedule: Optional[dict] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class ActivitySnapshot(BaseModel):
    open_tasks: int
    completed_tasks: int
    overdue_tasks: int
    recent_activity: List[dict] = []

class InvitationBase(BaseModel):
    email: EmailStr
    org_id: int
    role_id: Optional[int] = None

class InvitationCreate(InvitationBase):
    pass

class Invitation(InvitationBase):
    id: int
    token: str
    created_at: datetime
    expires_at: datetime
    is_used: bool
    org_name: Optional[str] = None
    role_name: Optional[str] = None

    class Config:
        from_attributes = True
