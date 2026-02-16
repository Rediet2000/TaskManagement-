from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import schemas, models
from app.api import deps
from app.db.base import get_db
from app.core.notifications import notification_service
import asyncio

router = APIRouter()

@router.get("/folders", response_model=List[schemas.notes.FolderOut])
def get_folders(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve folders for the current organization.
    """
    return db.query(models.notes.Folder).filter(
        models.notes.Folder.org_id == current_user.org_id
    ).all()

@router.post("/folders", response_model=schemas.notes.FolderOut)
def create_folder(
    *,
    db: Session = Depends(get_db),
    folder_in: schemas.notes.FolderCreate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create a new folder.
    """
    folder = models.notes.Folder(
        **folder_in.dict(),
        org_id=current_user.org_id,
        created_by=current_user.id
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder

@router.get("/", response_model=List[schemas.notes.NoteOut])
def get_notes(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    folder_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("updated_at"), # created_at, updated_at, title
    order: str = Query("desc")
) -> Any:
    """
    Retrieve notes for the current organization.
    """
    query = db.query(models.notes.Note).filter(
        models.notes.Note.org_id == current_user.org_id
    )

    # Permissions: User can edit own notes, Admin can view all
    # For MVP, let's assume all users in org can view but maybe only creator can edit?
    # Requirement: "User can edit own notes. Admin can view all notes."
    # Wait, the instruction says "Admin can view all notes" - does that mean non-admins ONLY view their own?
    # Usually in a team system, people expect to share? But I'll follow the rule.
    is_admin = current_user.role.name in ["Admin", "Super Admin"]
    if not is_admin:
        query = query.filter(models.notes.Note.created_by == current_user.id)

    if folder_id:
        query = query.filter(models.notes.Note.folder_id == folder_id)
    
    if search:
        query = query.filter(models.notes.Note.title.ilike(f"%{search}%"))

    # Sorting
    attr = getattr(models.notes.Note, sort_by, models.notes.Note.updated_at)
    if order == "desc":
        query = query.order_by(attr.desc())
    else:
        query = query.order_by(attr.asc())

    return query.all()

@router.post("/", response_model=schemas.notes.NoteOut)
def create_note(
    *,
    db: Session = Depends(get_db),
    note_in: schemas.notes.NoteCreate,
    background_tasks: BackgroundTasks,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create a new note.
    """
    note = models.notes.Note(
        **note_in.dict(),
        org_id=current_user.org_id,
        created_by=current_user.id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # Notify via Telegram
    background_tasks.add_task(
        notification_service.send_telegram_background,
        current_user.org_id, 
        f"📝 New Note: {note.title}\nBy: {current_user.full_name}"
    )

    return note

@router.get("/{id}", response_model=schemas.notes.NoteOut)
def get_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get a specific note.
    """
    note = db.query(models.notes.Note).filter(
        models.notes.Note.id == id,
        models.notes.Note.org_id == current_user.org_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    is_admin = current_user.role.name in ["Admin", "Super Admin"]
    if not is_admin and note.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return note

@router.put("/{id}", response_model=schemas.notes.NoteOut)
def update_note(
    *,
    id: int,
    db: Session = Depends(get_db),
    note_in: schemas.notes.NoteUpdate,
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update a note.
    """
    note = db.query(models.notes.Note).filter(
        models.notes.Note.id == id,
        models.notes.Note.org_id == current_user.org_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    if note.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own notes")
        
    update_data = note_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
        
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{id}")
def delete_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete a note.
    """
    note = db.query(models.notes.Note).filter(
        models.notes.Note.id == id,
        models.notes.Note.org_id == current_user.org_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    if note.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own notes")
        
    db.delete(note)
    db.commit()
    return {"status": "success"}
