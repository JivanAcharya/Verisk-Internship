from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data:dict):
    to_encode= data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes = settings.access_token_expire_time)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.hashing_algorithm)
    return encoded_jwt

def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str):
    return pwd_context.hash(password)

##later put in a separate deps.py file


