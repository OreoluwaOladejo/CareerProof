# app/routers/profiles.py
# The router only translates HTTP into service calls and service
# exceptions into HTTP errors. No business rules live here.
#
# Both endpoints use /me. The profile is found through the TOKEN, so
# there is no id in the URL for anyone to change.

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileResponse
from app.schemas.profile import ProfileUpdate
from app.services.profile import ProfileNotFound
from app.services.profile import get_profile
from app.services.profile import update_profile

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
)


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def read_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Depends(get_current_user) is the protection: no valid token means
    # 401 and this function never runs.
    try:
        return get_profile(db, current_user)
    except ProfileNotFound:
        # Should never happen, because registration creates the profile.
        # If it does, the client gets a clean 404 instead of a crash.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )


@router.patch(
    "/me",
    response_model=ProfileResponse,
)
def update_my_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # data is validated by ProfileUpdate BEFORE this function runs, so
    # bad URLs and too-long values are already rejected with a 422.
    try:
        return update_profile(db, current_user, data)
    except ProfileNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )