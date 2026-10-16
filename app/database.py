from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# The engine is SQLAlchemy's main connection point to PostgreSQL.

engine = create_engine(
    settings.database_url
)



# sessionmaker is a factory that creates these sessions.

SessionLocal = sessionmaker(
    bind=engine,

    # Prevent SQLAlchemy from automatically flushing changes
    autoflush=False,

    # Keep objects usable after commit.
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

# 1. Creates a database session.
# 2. Gives that session to our endpoint.
# 3. Closes the session when the request is finished.

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()