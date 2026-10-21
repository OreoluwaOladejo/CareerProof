from fastapi import FastAPI

from app.config import settings
from app.routers import auth
from app.routers import users

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# The version lives in the path, as agreed in the design doc.
app.include_router(
    auth.router,
    prefix="/api/v1",
)
app.include_router(
    users.router,
    prefix="/api/v1",
)


@app.get("/health")
def health():
    # Used by hosting platforms to check the app is alive.
    return {"status": "ok"}