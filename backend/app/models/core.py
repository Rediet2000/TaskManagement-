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
    
    users = relationship("User", back_populates="organization")
    departments = relationship("Department", back_populates="organization")
    roles = relationship("Role", back_populates="organization")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    
    organization = relationship("Organization", back_populates="departments")
    teams = relationship("Team", back_populates="department")

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dept_id = Column(Integer, ForeignKey("departments.id"))
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    department = relationship("Department", back_populates="teams")
    members = relationship("User", back_populates="team", foreign_keys="User.team_id")

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
    team_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Note: Fixed team_id FK below
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="users")
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
