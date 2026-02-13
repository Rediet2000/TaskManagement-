from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.task_tracking import Task, GitCommit
import re

router = APIRouter()

@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Receive push events from GitHub.
    Expected payload contains 'commits' array.
    """
    payload = await request.json()
    
    if "commits" not in payload:
        return {"status": "ignored", "reason": "no commits found"}

    processed_commits = 0
    for commit_data in payload["commits"]:
        message = commit_data.get("message", "")
        # Look for task ID in format #123
        match = re.search(r"#(\d+)", message)
        
        if match:
            task_id = int(match.group(1))
            # Verify task exists
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                new_commit = GitCommit(
                    hash=commit_data.get("id", "unknown")[:7],
                    message=message,
                    author=commit_data.get("author", {}).get("name", "Unknown"),
                    url=commit_data.get("url"),
                    task_id=task_id
                )
                db.add(new_commit)
                processed_commits += 1
    
    db.commit()
    return {"status": "success", "processed_commits": processed_commits}
