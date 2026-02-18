from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    folder_id: Optional[int] = None
    reminder_at: Optional[datetime] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    folder_id: Optional[int] = None
    reminder_at: Optional[datetime] = None

class NoteOut(NoteBase):
    id: int
    org_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FolderBase(BaseModel):
    name: str

class FolderCreate(FolderBase):
    pass

class FolderOut(FolderBase):
    id: int
    org_id: int
    created_by: int
    created_at: datetime
    notes: List[NoteOut] = []

    class Config:
        from_attributes = True
