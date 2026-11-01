from fastapi import APIRouter

from app.routers import auth
from app.routers import profile
from app.routers import users

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(users.router)