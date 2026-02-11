from fastapi import APIRouter
from app.api.v1.endpoints import auth, rbac, tasks, problems, hierarchy, reports, sprints

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(rbac.router, prefix="/rbac", tags=["rbac"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(problems.router, prefix="/problems", tags=["problems"])
api_router.include_router(hierarchy.router, prefix="/hierarchy", tags=["hierarchy"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(sprints.router, prefix="/sprints", tags=["sprints"])
