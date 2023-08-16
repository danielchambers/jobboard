import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from application.config import settings

database_url = f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@postgres:5432/{settings.POSTGRES_DATABASE}'
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
