from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class TaskStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    STARTED = "Started"
    PENDING = "Pending"
    COMPLETED = "Completed"

class TaskPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TaskFrequency(str, enum.Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    priority = Column(String, default=TaskPriority.MEDIUM)
    frequency = Column(String, default=TaskFrequency.DAILY)
    category = Column(String, nullable=True)
    status = Column(String, default=TaskStatus.NOT_STARTED)
    
    creator_id = Column(Integer, ForeignKey("users.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProblemArea(Base):
    __tablename__ = "problem_areas"

    id = Column(Integer, primary_key=True, index=True)
    branch_location = Column(String, index=True)
    problem_type = Column(String)
    customer_name = Column(String, nullable=True)
    status = Column(String, default="Open") # Open, In Progress, Fixed
    
    assigned_person_id = Column(Integer, ForeignKey("users.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))
    
    assigned_date = Column(DateTime(timezone=True), server_default=func.now())
    fixed_date = Column(DateTime(timezone=True), nullable=True)
    resolution_time = Column(Float, nullable=True) # in hours or minutes

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel = Column(String) # web, email, telegram
    message = Column(Text)
    status = Column(String, default="Pending") # Pending, Sent, Failed
    trigger_event = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
