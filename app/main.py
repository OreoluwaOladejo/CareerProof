from fastapi import FastAPI

from app.api import api_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# Every feature router arrives through this single include.
app.include_router(api_router)


@app.get("/health")
def health():
    # Used by hosting platforms to check the app is alive.
    return {"status": "ok"}