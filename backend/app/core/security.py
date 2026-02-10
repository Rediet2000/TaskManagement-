from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "purpose": "access"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_password_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"exp": expire, "sub": email, "purpose": "reset"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
