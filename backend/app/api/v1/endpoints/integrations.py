from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app import schemas, models
from app.api import deps

router = APIRouter()

@router.get("/github", response_model=schemas.integrations.GitHubIntegrationOut)
def get_github_integration(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get GitHub integration status for the current organization.
    """
    integration = db.query(models.integrations.GitHubIntegration).filter(
        models.integrations.GitHubIntegration.org_id == current_user.org_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="GitHub integration not found for this organization")
    
    return integration

@router.post("/github", response_model=schemas.integrations.GitHubIntegrationOut)
def create_or_update_github_integration(
    integration_in: schemas.integrations.GitHubIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create or update GitHub integration.
    """
    # Only admins can manage integrations
    if current_user.role.name not in ["Admin", "Super Admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    integration = db.query(models.integrations.GitHubIntegration).filter(
        models.integrations.GitHubIntegration.org_id == current_user.org_id
    ).first()
    
    if not integration:
        integration = models.integrations.GitHubIntegration(
            org_id=current_user.org_id,
            **integration_in.dict()
        )
        db.add(integration)
    else:
        for field, value in integration_in.dict().items():
            setattr(integration, field, value)
    
    db.commit()
    db.refresh(integration)
    return integration

@router.post("/github/repositories", response_model=schemas.integrations.GitHubRepoOut)
def register_repository(
    repo_in: schemas.integrations.GitHubRepoBase,
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Register a GitHub repository for tracking.
    """
    if current_user.role.name not in ["Admin", "Super Admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    integration = db.query(models.integrations.GitHubIntegration).filter(
        models.integrations.GitHubIntegration.org_id == current_user.org_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=400, detail="Initialize GitHub integration first")

    # Check if repo exists
    repo = db.query(models.integrations.GitHubRepository).filter(
        models.integrations.GitHubRepository.github_id == repo_in.github_id
    ).first()
    
    if repo:
        if repo.integration_id != integration.id:
            raise HTTPException(status_code=400, detail="Repository already registered to another organization")
        return repo

    repo = models.integrations.GitHubRepository(
        integration_id=integration.id,
        **repo_in.dict()
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo

@router.get("/github/activity", response_model=List[schemas.integrations.GitHubActivityOut])
def get_github_activity(
    db: Session = Depends(get_db),
    current_user: models.core.User = Depends(deps.get_current_active_user),
    limit: int = 20
) -> Any:
    """
    Get recent GitHub activities for the organization.
    """
    return db.query(models.integrations.GitHubActivity).filter(
        models.integrations.GitHubActivity.org_id == current_user.org_id
    ).order_by(models.integrations.GitHubActivity.timestamp.desc()).limit(limit).all()
