from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from app.db.session import engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import  User
from app.schemas import Token,TokenPayload
from app.core.config import settings

reusable_oauth2  = OAuth2PasswordBearer(
    tokenUrl = "api/v1/login/access-token"
)

# Session = sessionmaker(
#     bind = engine,
#     autocommit = False,
#     autoflush = False
# )


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(token:TokenDep,db:SessionDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.hashing_algorithm]
        )
        token_data = TokenPayload(**payload)
    except(InvalidTokenError,ValidationError):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    # get takes the second parameter as the primary key
    # user = session.get(User, token_data.user_id)

    user = db.query(User).filter(User.user_id== token_data.user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
