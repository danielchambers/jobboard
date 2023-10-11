from sqlalchemy import create_engine, Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from application.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(75))
    lastname = Column(String(75))
    password = Column(String(75))
    email = Column(String(75), unique=True, index=True)
    is_staff = Column(Boolean, default=False)
    is_member = Column(Boolean, default=False)
    jobs_watched = relationship("UserJobWatched", back_populates="user")
    jobs_applied = relationship("UserJobApplied", back_populates="user")


class UserJobWatched(Base):
    __tablename__ = 'users_jobs_watched'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(String(100), nullable=False)
    platform = Column(String(75), nullable=False)
    date_added = Column(TIMESTAMP, default=func.now())
    user = relationship("User", back_populates="jobs_watched")


class UserJobApplied(Base):
    __tablename__ = 'users_jobs_applied'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(String(100), nullable=False)
    platform = Column(String(75), nullable=False)
    date_added = Column(TIMESTAMP, default=func.now())
    rejected = Column(Boolean, default=False)
    date_rejected = Column(TIMESTAMP)
    accepted = Column(Boolean, default=False)
    date_accepted = Column(TIMESTAMP)
    offer_amount = Column(Integer)
    user = relationship("User", back_populates="jobs_applied")
