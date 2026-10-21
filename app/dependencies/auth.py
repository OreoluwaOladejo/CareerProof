from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

# This object does two jobs:
# 1. It reads the token out of the "Authorization: Bearer <token>" header.
#    If the header is missing, FastAPI automatically answers 401.
# 2. It tells /docs where the login endpoint is, which is what makes the
#    "Authorize" button work in the browser.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    # The same error is used for every failure, so a caller learns
    # nothing about WHY the token was rejected.
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        # Expired, tampered with, forged, or garbage.
        raise credentials_error

    # We load the user from the database on every request instead of
    # trusting the token alone. That way a user who has been deleted or
    # deactivated since the token was issued is rejected immediately.
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error

    return user