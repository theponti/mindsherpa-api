from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.utils.config import settings
from src.utils.logger import logger

engine = create_engine(settings.DATABASE_URL, echo=True)

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


# connect_to_db()
