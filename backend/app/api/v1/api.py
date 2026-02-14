from fastapi import APIRouter
from app.api.v1.endpoints import auth, rbac, tasks, problems, hierarchy, reports, sprints, webhooks, profile, notes, integrations, notifications, security, agile

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(rbac.router, prefix="/rbac", tags=["rbac"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(agile.router, prefix="/agile", tags=["agile"])
api_router.include_router(problems.router, prefix="/problems", tags=["problems"])
api_router.include_router(hierarchy.router, prefix="/hierarchy", tags=["hierarchy"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(sprints.router, prefix="/sprints", tags=["sprints"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(security.router, prefix="/security", tags=["security"])
