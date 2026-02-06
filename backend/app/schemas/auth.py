from typing import Optional
from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    org_id: Optional[int] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    org_id: int

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_verified: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

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
        orm_mode = True
