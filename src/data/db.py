import os

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.utils.logger import logger

DATABASE_URL = os.environ.get(
    "DATABASE_URL", default="postgresql+psycopg2://postgres:postgres@postgres:5432/postgres"
)

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Session
Session = sessionmaker(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def connect_to_db():
    try:
        connection = engine.connect()
        logger.info("Successfully connected to the database!")
        connection.close()
    except Exception as e:
        logger.error(f"An error occurred: {e}")


connect_to_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# You can use this as a dependency in your FastAPI routes
def get_db_dependency():
    return Depends(get_db)
