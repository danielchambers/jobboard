from sqlalchemy import Column, Integer, String, Boolean, ARRAY, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB
from sqlalchemy.schema import UniqueConstraint
from datetime import datetime
from application.database import Base


# class Company(Base):
#     __tablename__ = 'companies'

#     id = Column(Integer, primary_key=True)
#     company = Column(String(75), unique=True)
#     url = Column(String(150))
#     platform = Column(String(100))
#     total_jobs = Column(Integer, default=0)
#     found_date = Column(TIMESTAMP, default=func.now())
#     is_active = Column(Boolean, default=True)

#     jobs = relationship("Job", back_populates="company")


# class Job(Base):
#     __tablename__ = 'jobs'

#     id = Column(Integer, primary_key=True)
#     company_id = Column(Integer, ForeignKey('companies.id'))
#     title = Column(String(150))
#     url = Column(String(150))
#     country = Column(String(100))
#     state = Column(String(100))
#     city = Column(String(100))
#     is_remote = Column(Boolean, default=False)
#     is_hybrid = Column(Boolean, default=False)
#     post_date = Column(TIMESTAMP)
#     identifier = Column(String(100))

#     company = relationship("Company", back_populates="jobs")


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(75))
    url = Column(String(150))
    total_jobs = Column(Integer, default=0)
    platform = Column(String(100))
    found_date = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    # Define a unique constraint using 'name' instead of 'company'
    __table_args__ = (
        (UniqueConstraint('name', 'platform', name='uq_company_platform')),
    )

    # Establish a one-to-many relationship with the "jobs" table
    jobs = relationship('Job', back_populates='company')


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    job_id = Column(String(100))
    title = Column(String(255))
    country = Column(ARRAY(String(255)))
    state = Column(ARRAY(String(255)))
    city = Column(ARRAY(String(255)))
    is_remote = Column(Boolean, default=False)
    is_hybrid = Column(Boolean, default=False)
    is_onsite = Column(Boolean, default=False)
    salary = Column(JSONB, nullable=True)
    keywords = Column(ARRAY(String(255)))
    updated_at = Column(DateTime)
    url = Column(String(255))
    title_vector = Column(TSVECTOR)

    # Establish a many-to-one relationship with the "companies" table
    company = relationship('Company', back_populates='jobs')
