from collections.abc import Generator
from typing import Annotated

from jose import jwt,JWTError
# import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from jwt import InvalidTokenError
from pydantic import ValidationError
from app.db.session import engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import  User
from app.schemas import Token,TokenPayload
from app.core.config import settings
from app.core.security import decode_token, token_expired

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
        print("\n TOKEN IN QUERY: ",token)
        if token_expired(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is expired.")

        token_data = decode_token(token)
        # print(token_data)
    except(JWTError,ValidationError):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    # get takes the second parameter as the primary key
    # user = session.get(User, token_data.user_id)

    user = db.query(User).filter(User.email== token_data['sub']).first()
    # print("\n Inside get_current_user , User info :: ",user)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
