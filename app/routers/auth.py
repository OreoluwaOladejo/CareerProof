from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.schemas.user import UserResponse
from app.services.auth_service import EmailAlreadyRegistered
from app.services.auth_service import InvalidCredentials
from app.services.auth_service import authenticate_user
from app.services.auth_service import register_user
from app.utils.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    # user_in is validated by UserCreate BEFORE this function runs.
    # response_model=UserResponse means FastAPI filters whatever we
    # return down to the fields in UserResponse, so password_hash can
    # never leave the API.
    try:
        return register_user(db, user_in)
    except EmailAlreadyRegistered:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Login arrives as form data (decision D1). The form's "username"
    # field carries the email.
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(user.id))