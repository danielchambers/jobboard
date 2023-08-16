import datetime
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from application.database import Base


class GreenhouseCompany(Base):
    __tablename__ = 'greenhouse_companies'

    id = Column(Integer, primary_key=True)
    identifier = Column(String(75), unique=True)
    company = Column(String(75))
    website = Column(String(100))
    found_date = Column(TIMESTAMP, server_default='NOW()')
    is_active = Column(Boolean, default=True)
    total_jobs = Column(Integer, default=0)

    jobs = relationship('GreenhouseJob', back_populates='company')


class GreenhouseJob(Base):
    __tablename__ = 'greenhouse_jobs'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('greenhouse_companies.id'))
    title = Column(String(150))
    location = Column(String(25))
    job_id = Column(String(25))
    listing_date = Column(TIMESTAMP)

    company = relationship('GreenhouseCompany', back_populates='jobs')


class LeverCompany(Base):
    __tablename__ = 'lever_companies'

    id = Column(Integer, primary_key=True)
    identifier = Column(String(75), unique=True)
    company = Column(String(75))
    website = Column(String(100))
    found_date = Column(TIMESTAMP, server_default='NOW()')
    is_active = Column(Boolean, default=True)
    total_jobs = Column(Integer, default=0)

    jobs = relationship('LeverJob', back_populates='company')


class LeverJob(Base):
    __tablename__ = 'lever_jobs'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('lever_companies.id'))
    title = Column(String(150))
    location = Column(String(25))
    job_id = Column(String(25))
    listing_date = Column(TIMESTAMP)

    company = relationship('LeverCompany', back_populates='jobs')


class MyWorkdayJobsCompany(Base):
    __tablename__ = 'myworkdayjob_companies'

    id = Column(Integer, primary_key=True)
    identifier = Column(String(75), unique=True)
    company = Column(String(75))
    website = Column(String(100))
    found_date = Column(TIMESTAMP, server_default='NOW()')
    is_active = Column(Boolean, default=True)
    total_jobs = Column(Integer, default=0)

    jobs = relationship('MyWorkdayJob', back_populates='company')


class MyWorkdayJob(Base):
    __tablename__ = 'myworkdayjob_jobs'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('myworkdayjob_companies.id'))
    title = Column(String(150))
    location = Column(String(25))
    job_id = Column(String(25))
    listing_date = Column(TIMESTAMP)

    company = relationship('MyWorkdayJobsCompany', back_populates='jobs')
