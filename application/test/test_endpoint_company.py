import os
import pytest
from application.v1.companies import companies_router

BASE_URL = '/v1/companies'
os.environ['FASTAPI_CONFIG'] = "testing"


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
def client(application):
    from fastapi.testclient import TestClient

    yield TestClient(application)


def test_return_all_company_names(client):
    response = client.get(F'{BASE_URL}/')
    assert response.status_code == 200
    assert response.json() == {'endpoint': '/'}


def test_return_all_company_names_with_query(client):
    query = 'netflix'
    page = 1
    limit = 10
    response = client.get(
        f"{BASE_URL}/?q={query}&page={page}&limit={limit}")
    assert response.status_code == 200
    assert response.json() == {
        'endpoint': f'/q={query}&page={page}&limit={limit}'}


def test_return_one_company_name(client):
    company_name = "example_company"
    response = client.get(f'{BASE_URL}/{company_name}')
    assert response.status_code == 200
    assert response.json() == {'endpoint': company_name}
