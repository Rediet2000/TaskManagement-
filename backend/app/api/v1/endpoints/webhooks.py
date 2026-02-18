from typing import Any, List
import hmac
import hashlib
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.task_tracking import Task, GitCommit
from app.models.integrations import GitHubIntegration, GitHubRepository, GitHubPullRequest, GitHubActivity
from app.models.core import User

router = APIRouter()

async def verify_signature(request: Request, secret: str):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        return False
    
    body = await request.body()
    expected_signature = "sha256=" + hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    db: Session = Depends(get_db)
) -> Any:
    """
    Comprehensive GitHub Webhook Handler
    Handles: push, pull_request, issues, release
    """
    payload = await request.json()
    github_repo_id = payload.get("repository", {}).get("id")
    
    if not github_repo_id:
        return {"status": "ignored", "reason": "no repository info"}

    # Find the integration linked to this repository
    repo = db.query(GitHubRepository).filter(GitHubRepository.github_id == github_repo_id).first()
    if not repo:
        return {"status": "ignored", "reason": "repository not registered in system"}
    
    integration = repo.integration
    org_id = integration.org_id

    # Verify signature if secret is set
    if integration.webhook_secret:
        if not await verify_signature(request, integration.webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")

    actor = payload.get("sender", {}).get("login", "unknown")

    if x_github_event == "push":
        return await handle_push(payload, repo, org_id, db)
    
    elif x_github_event == "pull_request":
        return await handle_pull_request(payload, repo, org_id, db)
    
    elif x_github_event == "issues":
        return await handle_issues(payload, repo, org_id, db)
    
    elif x_github_event == "release":
        return await handle_release(payload, repo, org_id, db)

    return {"status": "ignored", "event": x_github_event}

async def handle_push(payload: Any, repo: GitHubRepository, org_id: int, db: Session):
    processed_commits = 0
    commits_data = payload.get("commits", [])
    
    for commit_data in commits_data:
        message = commit_data.get("message", "")
        # Look for task ID in format #123 or [TASK-123]
        match = re.search(r"#(\d+)", message)
        
        if match:
            task_id = int(match.group(1))
            task = db.query(Task).filter(Task.id == task_id, Task.org_id == org_id).first()
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

    # Log activity
    activity = GitHubActivity(
        org_id=org_id,
        event_type="push",
        actor=payload.get("sender", {}).get("login"),
        content=f"Pushed {len(commits_data)} commits to {repo.name}",
        url=payload.get("compare"),
        github_payload=payload
    )
    db.add(activity)
    db.commit()
    
    return {"status": "success", "processed_commits": processed_commits}

async def handle_pull_request(payload: Any, repo: GitHubRepository, org_id: int, db: Session):
    action = payload.get("action")
    pr_data = payload.get("pull_request")
    pr_number = pr_data.get("number")
    
    # Sync PR to database
    pr = db.query(GitHubPullRequest).filter(
        GitHubPullRequest.repo_id == repo.id,
        GitHubPullRequest.number == pr_number
    ).first()
    
    if not pr:
        pr = GitHubPullRequest(
            repo_id=repo.id,
            github_id=pr_data.get("id"),
            number=pr_number,
            title=pr_data.get("title"),
            state=pr_data.get("state"),
            html_url=pr_data.get("html_url"),
            author=pr_data.get("user", {}).get("login")
        )
        db.add(pr)
    else:
        pr.title = pr_data.get("title")
        pr.state = pr_data.get("state")
        if action == "closed" and pr_data.get("merged"):
            pr.state = "merged"
            pr.merged_at = func.now()

    # Auto-link to task if title contains #123
    match = re.search(r"#(\d+)", pr.title)
    if match:
        task_id = int(match.group(1))
        task = db.query(Task).filter(Task.id == task_id, Task.org_id == org_id).first()
        if task:
            pr.task_id = task_id

    # Log activity
    activity = GitHubActivity(
        org_id=org_id,
        event_type="pull_request",
        actor=payload.get("sender", {}).get("login"),
        content=f"{action.capitalize()} PR #{pr_number}: {pr.title}",
        url=pr.html_url,
        github_payload=payload
    )
    db.add(activity)
    db.commit()
    
    return {"status": "success", "action": action}

async def handle_issues(payload: Any, repo: GitHubRepository, org_id: int, db: Session):
    action = payload.get("action")
    issue_data = payload.get("issue")
    
    activity = GitHubActivity(
        org_id=org_id,
        event_type="issue",
        actor=payload.get("sender", {}).get("login"),
        content=f"{action.capitalize()} issue #{issue_data.get('number')}: {issue_data.get('title')}",
        url=issue_data.get("html_url"),
        github_payload=payload
    )
    db.add(activity)
    db.commit()
    return {"status": "success"}

async def handle_release(payload: Any, repo: GitHubRepository, org_id: int, db: Session):
    action = payload.get("action")
    release_data = payload.get("release")
    
    activity = GitHubActivity(
        org_id=org_id,
        event_type="release",
        actor=payload.get("sender", {}).get("login"),
        content=f"{action.capitalize()} release {release_data.get('tag_name')}: {release_data.get('name')}",
        url=release_data.get("html_url"),
        github_payload=payload
    )
    db.add(activity)
    db.commit()
    return {"status": "success"}
