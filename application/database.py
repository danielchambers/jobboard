import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, declarative_base
from application.config import settings

database_url = f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@postgres:5432/{settings.POSTGRES_DATABASE}'
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def database_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except IntegrityError:
        logger.warning("Integrity error occurred. Rolling back.")
        session.rollback()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        session.rollback()
        raise
    finally:
        session.close()


database_context = contextmanager(database_session)
