from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class GitHubIntegration(Base):
    __tablename__ = "github_integrations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), unique=True)
    installation_id = Column(String, nullable=True) # For GitHub Apps
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    webhook_secret = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization")
    repositories = relationship("GitHubRepository", back_populates="integration", cascade="all, delete-orphan")

class GitHubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("github_integrations.id"))
    github_id = Column(Integer, unique=True)
    name = Column(String)
    full_name = Column(String)
    html_url = Column(String)
    is_private = Column(Boolean, default=False)
    
    integration = relationship("GitHubIntegration", back_populates="repositories")

class GitHubPullRequest(Base):
    __tablename__ = "github_pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("github_repositories.id"))
    github_id = Column(Integer)
    number = Column(Integer)
    title = Column(String)
    state = Column(String) # open, closed, merged
    html_url = Column(String)
    author = Column(String)
    merged_at = Column(DateTime(timezone=True), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    repository = relationship("GitHubRepository")
    task = relationship("Task")

class GitHubActivity(Base):
    __tablename__ = "github_activities"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    event_type = Column(String) # push, pull_request, issues, release
    actor = Column(String)
    content = Column(Text)
    url = Column(String, nullable=True)
    github_payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization")
