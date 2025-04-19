from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import User
from app.api.deps import get_db, TokenDep
from app.schemas import UserRegisterSchema,UserLoginSchema, Token
from app.api.routes import crud
from app.core.security import create_access_token
from app.utils import generate_new_account_email, send_email

router = APIRouter(tags=["auth"],prefix ="/api/v1/auth")
 
@router.post("/register",status_code=status.HTTP_201_CREATED )
def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    print(type(UserRegisterSchema))
    existing_user = crud.get_user_by_email(db = db, email = user.email)
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "The user with this email already exists in the system"
        )

    user_create = UserRegisterSchema.model_validate(user)

    user = crud.create_user(db= db, user_create = user_create)
    
    print("\n ********  USER CREATED *********")

    if user.email:
        email_data = generate_new_account_email(
            email_to=user.email, username=user.username
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    print("\n ********  EMAIL SENT *********")
    return { 
        "message":"User Registered Successfully",
        "user":{
            "username":user.username,
            "email":user.email,
        }
    }

@router.post("/login/access-token",status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session=  Depends(get_db)) -> Token:
    """
    Login a user and returns a jwt token
    """
    user = crud.authenticate(db= db, email = form_data.username, password = form_data.password)
    # print(user)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password",
            headers = {"WWW-Authenticate":"Bearer"},
        )
    
    access_token = create_access_token(data = {"sub":user.email})
    return Token(access_token=access_token)

