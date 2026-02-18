from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class GitHubRepoBase(BaseModel):
    github_id: int
    name: str
    full_name: str
    html_url: str
    is_private: bool

class GitHubRepoOut(GitHubRepoBase):
    id: int
    
    class Config:
        from_attributes = True

class GitHubIntegrationBase(BaseModel):
    installation_id: Optional[str] = None
    webhook_secret: Optional[str] = None

class GitHubIntegrationCreate(GitHubIntegrationBase):
    pass

class GitHubIntegrationUpdate(GitHubIntegrationBase):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

class GitHubIntegrationOut(GitHubIntegrationBase):
    id: int
    org_id: int
    created_at: datetime
    updated_at: datetime
    repositories: List[GitHubRepoOut] = []

    class Config:
        from_attributes = True

class GitHubActivityOut(BaseModel):
    id: int
    event_type: str
    actor: str
    content: str
    url: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
