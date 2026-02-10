from typing import Optional
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
    dept_name: Optional[str] = None
    team_name: Optional[str] = None

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

class OrganizationCreate(OrganizationBase):
    name: str

class Organization(OrganizationBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True
