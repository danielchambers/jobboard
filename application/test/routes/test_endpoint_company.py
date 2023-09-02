from application.models.jobs import Company

BASE_URL = '/v1/companies'


def test_database(company_dataset):
    company_dataset.commit()
    assert len(company_dataset.query(Company).all()) == 6


def test_return_all_company_names_paginate(client, company_dataset):
    company_dataset.commit()
    response = client.get(F'{BASE_URL}/?page=1&limit=6')
    assert response.status_code == 200
    assert response.json()['total'] == 6


def test_return_all_company_names_query(client, company_dataset):
    company_dataset.commit()
    response = client.get(F'{BASE_URL}/?q=pay')
    assert response.status_code == 200
    assert response.json()['total'] == 2
    assert response.json()['results'][0]['company'] == 'wepay'
    assert response.json()['results'][1]['company'] == 'netpay'


def test_return_all_company_names_query_page_limit(client, company_dataset):
    company_dataset.commit()
    response = client.get(F'{BASE_URL}/?q=pay&page=1&limit=1')
    assert response.status_code == 200
    assert response.json()['total'] == 2
    assert response.json()['results'][0]['company'] == 'wepay'


def test_return_all_company_names(client, company_dataset):
    company_dataset.commit()
    response = client.get(F'{BASE_URL}/')
    assert response.status_code == 200
    assert response.json()['total'] == 6
    assert response.json()['results'][0]['company'] == 'netflix'


def test_return_one_company_name(client, company_dataset):
    company_dataset.commit()

    company_name = "netflix"
    response = client.get(f'{BASE_URL}/{company_name}')
    assert response.status_code == 200
    assert response.json()['total'] == 1
    assert response.json()['results'][0]['company'] == company_name
