from typing import Optional, List
from pydantic import BaseModel

class OrganizationBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    primary_color: str = "#1e293b"
    secondary_color: str = "#38bdf8"
    email_domain: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    
    # Password & Session Settings
    password_min_length: int = 8
    password_require_special: bool = True
    password_expiry_days: int = 90
    session_timeout_minutes: int = 60
    
    # LDAP Settings
    ldap_enabled: bool = False
    ldap_server: Optional[str] = None
    ldap_base_dn: Optional[str] = None
    
    # Notification Settings
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_enabled: bool = False
    email_notifications_enabled: bool = True
    
    # Branding Settings
    system_page_title: str = "Task Management System"
    theme_mode: str = "system"
    
    # Company Profile (Phase 15)
    industry: Optional[str] = None
    address: Optional[str] = None
    timezone: str = "UTC"
    default_language: str = "en"
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

    # Dashboard Settings
    show_dashboard_clock: bool = True
    show_dashboard_map: bool = False
    show_dashboard_stats: bool = True
    show_dashboard_tasks: bool = True
    
    dashboard_layout: str = "clock,stats,tasks,map"
    dashboard_refresh_rate: int = 30
    dashboard_clock_type: str = "analog"
    dashboard_metrics_config: str = "tasks,active,overdue,problems"
    dashboard_compact_mode: bool = False

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    email_domain: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    
    # Company Profile (Phase 15)
    industry: Optional[str] = None
    address: Optional[str] = None
    timezone: Optional[str] = None
    default_language: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    
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
    
    dashboard_layout: Optional[str] = None
    dashboard_refresh_rate: Optional[int] = None
    dashboard_clock_type: Optional[str] = None
    dashboard_metrics_config: Optional[str] = None
    dashboard_compact_mode: Optional[bool] = None

class Organization(OrganizationBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class BranchBase(BaseModel):
    name: str
    address: Optional[str] = None
    org_id: int

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

class Branch(BranchBase):
    id: int
    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    org_id: int
    branch_id: Optional[int] = None

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    
    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str
    dept_id: int
    org_id: int
    leader_id: Optional[int] = None

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    
    class Config:
        from_attributes = True

class AllowedDomainBase(BaseModel):
    domain: str
    org_id: int
    is_active: bool = True

class AllowedDomainCreate(AllowedDomainBase):
    pass

class AllowedDomain(AllowedDomainBase):
    id: int
    class Config:
        from_attributes = True

class MailListBase(BaseModel):
    email: str
    org_id: int
    is_active: bool = True

class MailListCreate(MailListBase):
    pass

class MailList(MailListBase):
    id: int
    class Config:
        from_attributes = True

class SMTPTest(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str
