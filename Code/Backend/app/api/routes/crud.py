import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models import User

from app.schemas import UserRegisterSchema


## the * in the first makes sure that the function is only called with named arguments
def create_user(*,db: Session, user_create: UserRegisterSchema) -> User:
    hashed_password = get_password_hash(user_create.password)

    db_user = User(
        username=user_create.username,
        email=user_create.email,
        password=hashed_password  
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)

    return db_user

def get_user_by_email(*,db: Session, email: str) -> User | None:
    # statement = select(User).where(User.email == email)
    # session_user = db.exec(statement).first()
    session_user = db.query(User).filter(User.email == email).first()
    return session_user

def authenticate(*, db: Session, email:str, password:str) -> User | None:
    user = get_user_by_email(db=db,email=email)
    print("Inside authenticate :: outside", user.email, user.password)
    if not user:
        # print("Inside authenticate :: user does not exist ", user)
        return None
    if not verify_password(password, user.password):
        # print("Inside authenticate :: password error ", password, )
        return None
    return user
