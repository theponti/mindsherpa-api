import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.logger import logger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")


engine = create_engine(DATABASE_URL, echo=True)
try:
    connection = engine.connect()
    logger.info("Successfully connected to the database!")
    connection.close()
except Exception as e:
    logger.error(f"An error occurred: {e}")


# Session
Session = sessionmaker(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
