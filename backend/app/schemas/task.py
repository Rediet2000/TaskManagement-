from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
import enum

class ModuleType(str, enum.Enum):
    CORE = "core"
    DEV = "dev"
    ADMIN = "admin"
    NET = "net"
    SALES = "sales"
    CRM = "crm"
    HR = "hr"
    SUPPORT = "support"

class IssueType(str, enum.Enum):
    TASK = "task"
    BUG = "bug"
    STORY = "story"
    EPIC = "epic"
    SUBTASK = "subtask"

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
    assigner_id: Optional[int] = None
    accountable_id: Optional[int] = None
    team_id: Optional[int] = None
    due_date: Optional[datetime] = None

    # Phase 8 Fields
    tags: List[str] = []
    module_type: ModuleType = ModuleType.CORE
    metadata_fields: dict = {}

    # Phase 9 Fields
    issue_type: IssueType = IssueType.TASK
    sprint_id: Optional[int] = None
    board_id: Optional[int] = None
    board_column_id: Optional[int] = None
    parent_id: Optional[int] = None
    story_points: Optional[int] = None
    estimated_hours: Optional[float] = None
    checklist: List[dict] = [] # list of {id: str, text: str, is_completed: bool}

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    category: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    assigner_id: Optional[int] = None
    accountable_id: Optional[int] = None
    team_id: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    module_type: Optional[ModuleType] = None
    metadata_fields: Optional[dict] = None
    issue_type: Optional[IssueType] = None
    sprint_id: Optional[int] = None
    parent_id: Optional[int] = None
    story_points: Optional[int] = None
    estimated_hours: Optional[float] = None
    board_id: Optional[int] = None
    board_column_id: Optional[int] = None
    checklist: Optional[List[dict]] = None
    
    # Phase 11
    rating: Optional[int] = None
    rating_comment: Optional[str] = None

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    task_id: int

class SprintBase(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: str = "Planning"

class SprintCreate(SprintBase):
    board_id: Optional[int] = None

class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    board_id: Optional[int] = None

class Sprint(SprintBase):
    id: int
    org_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Comment(CommentBase):
    id: int
    task_id: int
    author_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AttachmentBase(BaseModel):
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None

class AttachmentCreate(AttachmentBase):
    task_id: int
    file_path: str

class Attachment(AttachmentBase):
    id: int
    task_id: int
    uploader_id: int
    file_path: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GitCommit(BaseModel):
    id: int
    hash: str
    message: str
    author: str
    url: Optional[str] = None
    task_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class PullRequest(BaseModel):
    id: int
    number: int
    title: str
    state: str
    html_url: str
    author: str
    merged_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Task(TaskBase):
    id: int
    creator_id: int
    org_id: int
    created_at: datetime
    comments: List[Comment] = []
    attachments: List[Attachment] = []
    commits: List[GitCommit] = []
    pull_requests: List[PullRequest] = []
    
    completed_at: Optional[datetime] = None
    rating: Optional[int] = None
    rating_comment: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProblemAreaBase(BaseModel):
    branch_location: str
    component: Optional[str] = None
    device_id: Optional[str] = None
    problem_type: str
    severity: str = "Medium"
    customer_name: Optional[str] = None
    assigned_person_id: int
    branch_id: Optional[int] = None

class ProblemAreaCreate(ProblemAreaBase):
    pass

class ProblemArea(ProblemAreaBase):
    id: int
    status: str
    assigned_date: datetime
    fixed_date: Optional[datetime] = None
    resolution_time: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

class NotificationOut(BaseModel):
    id: int
    message: str
    status: str
    trigger_event: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLog(BaseModel):
    id: int
    user_id: int
    action: str
    details: Optional[str] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

# Phase 11: Reporting Schemas
class UserPerformance(BaseModel):
    user_id: int
    user_name: str
    tasks_assigned: int
    tasks_completed: int
    tasks_started: int
    avg_rating: Optional[float] = None
    on_time_rate: float # percentage

class TaskReportStats(BaseModel):
    total_tasks: int
    unassigned: int
    pending: int
    completed: int
    started: int
    user_performance: List[UserPerformance]
