import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_name = os.getenv('POSTGRES_DATABASE')
database_user = os.getenv('POSTGRES_USER')
database_password = os.getenv('POSTGRES_PASSWORD')
database_url = f'postgresql://{database_user}:{database_password}@postgres:5432/{database_name}'

engine = create_engine(database_url, echo=True)
Session = sessionmaker(bind=engine)
