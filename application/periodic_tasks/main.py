import random
from contextlib import contextmanager
from celery import shared_task
from application.database import SessionLocal
from .models import GreenhouseCompany


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


@shared_task
def test():
    random_value = random.random()
    new_company_data = {'name': random_value, 'jobs_available': 0}
    with get_db() as db:
        new_company = GreenhouseCompany(**new_company_data)
        db.add(new_company)
        db.commit()
        print(f'SAVED >>>> {random_value} <<<<')
