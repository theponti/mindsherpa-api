import os

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.utils.logger import logger

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
try:
    connection = engine.connect()
    logger.info("Successfully connected to the database!")
    connection.close()
except Exception as e:
    logger.error(f"An error occurred: {e}")

Base = declarative_base()

# Session
Session = sessionmaker(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# You can use this as a dependency in your FastAPI routes
def get_db_dependency():
    return Depends(get_db)
