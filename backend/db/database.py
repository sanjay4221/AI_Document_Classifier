from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.db.models import Base
from backend.core.logger import logger

# Use Neon PostgreSQL in production, SQLite locally
if settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logger.info("Using Neon PostgreSQL")
else:
    DATABASE_URL = "sqlite:///./classifier.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info("Using SQLite (local dev)")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialised")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
