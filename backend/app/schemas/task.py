from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
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

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    category: Optional[str] = None
    status: TaskStatus = TaskStatus.NOT_STARTED
    assignee_id: Optional[int] = None
    team_id: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    creator_id: int
    org_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProblemAreaBase(BaseModel):
    branch_location: str
    problem_type: str
    customer_name: Optional[str] = None
    assigned_person_id: int

class ProblemAreaCreate(ProblemAreaBase):
    pass

class ProblemArea(ProblemAreaBase):
    id: int
    status: str
    assigned_date: datetime
    fixed_date: Optional[datetime] = None
    resolution_time: Optional[float] = None
    
    class Config:
        orm_mode = True
