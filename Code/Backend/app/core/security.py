from datetime import datetime, timedelta, timezone, UTC
from typing import Any,Dict, Annotated
from fastapi import Depends, HTTPException, status
from app.api.deps import TokenDep
# import jwt
from jose import jwt,JWTError
from passlib.context import CryptContext

from app.core.config import settings
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_refresh_token(data:Dict[str, Any]) -> str:
    to_encode= data.copy()
    expires = datetime.now(timezone.utc) + timedelta(days = settings.refresh_token_expire_time)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.hashing_algorithm)
    return encoded_jwt

def create_access_token(data:Dict[str, Any]) -> str:
    to_encode= data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes = settings.access_token_expire_time)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.hashing_algorithm)
    return encoded_jwt

def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str):
    return pwd_context.hash(password)


def decode_token(token):
    return jwt.decode(token, settings.secret_key, algorithms=settings.hashing_algorithm)

def token_expired(token):
    try:
        payload = decode_token(token)
        if not datetime.fromtimestamp(payload.get('exp'), UTC) > datetime.now(UTC):
            return True
        return False

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")



