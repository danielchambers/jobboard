import requests


def get_greenhouse_jobs(company):
    headers = {

    }
    url = f'https://boards-api.greenhouse.io/v1/boards/{company}/jobs/'
    response = requests.get(url)
    return response.json()


def parse_greenhouse_job(company_id, job_data):
    return {
        'company_id': company_id,
        'title': job_data['title'],
        'location': job_data['location']['name'],
        'job_id': job_data['id'],
        'listing_date': job_data['updated_at'],
    }
