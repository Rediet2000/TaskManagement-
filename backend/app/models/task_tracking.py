from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum
from sqlalchemy.dialects.postgresql import JSONB

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
    
    # New Phase 8 Fields
    tags = Column(JSONB, default=[], nullable=False)
    module_type = Column(String, default=ModuleType.CORE)
    metadata_fields = Column(JSONB, default={}, nullable=False) # flexible storage for industry-specific data
    
    # Agile Phase 9 Fields
    issue_type = Column(String, default=IssueType.TASK)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True)
    board_column_id = Column(Integer, ForeignKey("board_columns.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True) # for epic/subtask relationships
    story_points = Column(Integer, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    checklist = Column(JSONB, default=[], nullable=False)
    
    creator_id = Column(Integer, ForeignKey("users.id"))
    assigner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    accountable_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Phase 11: Reports & Performance
    rating = Column(Integer, nullable=True) # 1-5 stars
    rating_comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
    commits = relationship("GitCommit", back_populates="task", cascade="all, delete-orphan")
    pull_requests = relationship("GitHubPullRequest", back_populates="task")
    
    creator = relationship("User", foreign_keys=[creator_id])
    assigner = relationship("User", foreign_keys=[assigner_id])
    accountable = relationship("User", foreign_keys=[accountable_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    team = relationship("Team")
    organization = relationship("Organization", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    board = relationship("Board", back_populates="tasks")
    board_column = relationship("BoardColumn", back_populates="tasks")

class GitCommit(Base):
    __tablename__ = "task_commits_git"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, index=True)
    message = Column(Text)
    author = Column(String)
    url = Column(String, nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="commits")

class Comment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Attachment(Base):
    __tablename__ = "task_attachments"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    uploader_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="attachments")
    uploader = relationship("User", back_populates="attachments")

class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    goal = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String, default="Planning") # Planning, Active, Completed
    org_id = Column(Integer, ForeignKey("organizations.id"))
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tasks = relationship("Task", back_populates="sprint")
    board = relationship("Board", back_populates="sprints")

class ProblemArea(Base):
    __tablename__ = "problem_areas"

    id = Column(Integer, primary_key=True, index=True)
    branch_location = Column(String, index=True)
    component = Column(String, index=True, nullable=True) # e.g. Network, Server, Elevator, etc.
    device_id = Column(String, nullable=True)
    problem_type = Column(String)
    severity = Column(String, default="Medium") # Low, Medium, High, Critical
    customer_name = Column(String, nullable=True)
    status = Column(String, default="Open") # Open, In Progress, Fixed
    
    assigned_person_id = Column(Integer, ForeignKey("users.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    
    assigned_date = Column(DateTime(timezone=True), server_default=func.now())
    fixed_date = Column(DateTime(timezone=True), nullable=True)
    resolution_time = Column(Float, nullable=True) # in hours or minutes

    assigned_person = relationship("User")
    organization = relationship("Organization", back_populates="problem_areas")
    branch = relationship("Branch", back_populates="problem_areas")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel = Column(String) # web, email, telegram
    message = Column(Text)
    status = Column(String, default="Pending") # Pending, Sent, Failed
    trigger_event = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

class TaskReport(Base):
    __tablename__ = "task_reports"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    report_type = Column(String) # Daily, Weekly, Monthly
    
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    pending_tasks = Column(Integer, default=0)
    efficiency_score = Column(Float, default=0.0) # 0 to 100
    rating = Column(Integer, default=0) # 1 to 5 stars
    
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    organization = relationship("Organization")
