import os
import pytest
from application.database import Base
from application.models.jobs import Company

os.environ["FASTAPI_CONFIG"] = "testing"


@pytest.fixture
def settings():
    from application.config import settings as application_settings

    return application_settings


@pytest.fixture
def application(settings):
    from application import create_app

    app = create_app()
    return app


@pytest.fixture()
def db_session():
    from application.database import Base, engine, SessionLocal

    Company()
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(application):
    from fastapi.testclient import TestClient

    yield TestClient(application)


@pytest.fixture()
def company_dataset(db_session):
    company_data_1 = {
        "company": "netflix",
        "url": "http://netflix.com",
        "platform": "greenhouse",
        "total_jobs": 100,
        "is_active": True,
    }
    company_data_2 = {
        "company": "google",
        "url": "http://google.com",
        "platform": "greenhouse",
        "total_jobs": 200,
        "is_active": True,
    }
    company_data_3 = {
        "company": "lyft",
        "url": "http://lyft.com",
        "platform": "greenhouse",
        "total_jobs": 300,
        "is_active": True,
    }
    company_data_4 = {
        "company": "airbnb",
        "url": "http://airbnb.com",
        "platform": "greenhouse",
        "total_jobs": 400,
        "is_active": True,
    }
    company_data_5 = {
        "company": "wepay",
        "url": "http://wepay.com",
        "platform": "greenhouse",
        "total_jobs": 500,
        "is_active": True,
    }
    company_data_6 = {
        "company": "netpay",
        "url": "http://netpay.com",
        "platform": "greenhouse",
        "total_jobs": 500,
        "is_active": True,
    }
    db_session.add_all([
        Company(**company_data_1), Company(**company_data_2),
        Company(**company_data_3), Company(**company_data_4),
        Company(**company_data_5), Company(**company_data_6)
    ])
    yield db_session
