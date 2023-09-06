import datetime
# from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ARRAY, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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
    company = Column(String(75))
    url = Column(String(150))
    total_jobs = Column(Integer, default=0)
    platform = Column(String(100))
    found_date = Column(TIMESTAMP, default=func.now())
    is_active = Column(Boolean, default=True)

    # Define a unique constraint
    __table_args__ = (
        (UniqueConstraint('company', 'platform', name='uq_company_platform')),
    )

    # Establish a one-to-many relationship with the "jobs" table
    jobs = relationship('Job', back_populates='company')


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    job_id = Column(String(100))
    title = Column(String(255))
    country = Column(String(100))
    state = Column(String(100))
    city = Column(String(100))
    is_remote = Column(Boolean, default=False)
    is_hybrid = Column(Boolean, default=False)
    is_onsite = Column(Boolean, default=True)
    salary_low = Column(Numeric)
    salary_high = Column(Numeric)
    keywords = Column(ARRAY(String(255)))
    updated_at = Column(DateTime)
    url = Column(String(255))

    # Establish a many-to-one relationship with the "companies" table
    company = relationship('Company', back_populates='jobs')
