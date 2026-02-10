from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
import os
import bcrypt
import passlib

print(f"--- Backend Startup: Bcrypt version {bcrypt.__version__}, Passlib version {passlib.__version__} ---")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if not os.path.exists(settings.STATIC_DIR):
    os.makedirs(settings.STATIC_DIR)
if not os.path.exists(settings.LOGOS_DIR):
    os.makedirs(settings.LOGOS_DIR)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

@app.get("/")
def root():
    return {"message": "Task Management API is running"}

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
