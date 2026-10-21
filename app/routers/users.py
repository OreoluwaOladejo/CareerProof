from fastapi import APIRouter
from fastapi import Depends

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_me(current_user: User = Depends(get_current_user)):
    # Depends(get_current_user) is the whole protection: if the token is
    # missing or invalid, FastAPI answers 401 and this function never
    # runs. If it does run, current_user is the verified logged-in user.
    return current_user