from fastapi import FastAPI
from app.config import settings
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

@app.get("/")
def root():
     return {
        "message": "CareerFlow API is running",
        "environment": settings.environment,
    }