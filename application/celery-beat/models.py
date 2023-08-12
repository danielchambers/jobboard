import datetime
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GreenhouseCompany(Base):
    __tablename__ = 'greenhouse_companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    timestamp_found = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    jobs_available = Column(Integer)


class LeverCompany(Base):
    __tablename__ = 'lever_companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    timestamp_found = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    jobs_available = Column(Integer)


class MyWorkdayJobsCompany(Base):
    __tablename__ = 'myworkdayjobs_companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    region = Column(String(5))
    uri = Column(String(50))
    timestamp_found = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    jobs_available = Column(Integer)
