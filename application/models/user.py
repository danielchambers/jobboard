from sqlalchemy import create_engine, Column, Integer, String, Boolean
from application.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(75))
    lastname = Column(String(75))
    password = Column(String(75))
    email = Column(String(75), unique=True, index=True)
    is_superuser = Column(Boolean, default=False)
