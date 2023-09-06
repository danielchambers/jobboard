import json
import redis
import logging
import asyncio
import aiohttp
import datetime
from celery import shared_task, current_task
from sqlalchemy import and_
from application.database import database_context
from application.models.jobs import Company as Company_Model
from application.models.jobs import Job as Job_Model
from application.periodic_tasks.task_utilities.company_finder import CompanyFinder
from application.periodic_tasks.task_utilities.company_jobs import Job as Job_Finder
from application.periodic_tasks.task_utilities.google_search import GoogleSearch

import requests
logging.basicConfig(level=logging.INFO)
redis_client = redis.Redis(host='redis', port=6379, db=1)


@shared_task
def company_names(job_platform, location, job_title):
    MAX_SERACH_RESULTS = 91
    PLATFORMS = {
        'greenhouse': {
            'search_query': 'site:boards.greenhouse.io {}',
            'url_pattern': r"boards\.greenhouse\.io\/(?P<company_name>\w+)",
            'url_format': 'https://boards-api.greenhouse.io/v1/boards/{}/jobs/',
        },
        'lever': {
            'search_query': 'site:jobs.lever.co {}',
            'url_pattern': r"jobs\.lever\.co\/(?P<company_name>\w+)",
            'url_format': 'https://jobs.lever.co/v0/postings/{}/?mode=json',
        },
        'careerpuck': {
            'search_query': 'site:app.careerpuck.com/job-board/ {}',
            'url_pattern': r"app\.careerpuck\.com\/job-board\/(?P<company_name>\w+)",
            'url_format': 'https://api.careerpuck.com/v1/public/job-boards/{}',
        },
        'ashbyhq': {
            'search_query': 'site:jobs.ashbyhq.com {}',
            'url_pattern': r"jobs\.ashbyhq\.com\/(?P<company_name>\w+)",
            'url_format': 'https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams',
        },
        'myworkdayjobs': {
            'search_query': 'site:myworkdayjobs.com {}',
            'url_pattern': r'(?P<company_name>\w+)\.(?P<company_region>\w+)\.myworkdayjobs\.com\/(?:[a-z]{2}-[A-Z]{2}\/)?(?P<company_uri>\w[\w\-]*|(?!.*\/)([^\/?#]+))',
            'url_format': 'https://{company_name}.{company_region}.myworkdayjobs.com/wday/cxs/{company_name}/{company_uri}/jobs',
        },
    }

    results = []
    page_index = 1
    page_results = 50
    query = PLATFORMS.get(job_platform).get(
        'search_query').format(f'{location} AND {job_title}')

    while True:
        search_results = GoogleSearch.search(query, page_index, page_results)
        if page_index >= MAX_SERACH_RESULTS:
            break
        if search_results.get('items') is None:
            break
        items = search_results.get('items')
        links = [item['link'].lower() for item in items if items]
        results.extend(links)
        page_index += page_results

    company_finder = CompanyFinder(job_platform, PLATFORMS.get(job_platform))
    companies = company_finder.parse(results)
    with database_context() as db:
        db.add_all([Company_Model(**company) for company in companies])


@shared_task
def collect_jobs():
    last_page = int(redis_client.get('last_page') or 1)
    page_size = 50
    offset = (last_page - 1) * page_size

    with database_context() as db:
        records = db.query(Company_Model).filter(and_(
            Company_Model.platform == 'greenhouse',
            Company_Model.is_active == True)
        ).offset(offset).limit(page_size).all()
        asyncio.run(main(records, db))

    if len(records) < page_size:
        last_page = 1
    else:
        last_page += 1
        current_task.apply_async(countdown=60)

    redis_client.set('last_page', last_page)


async def main(records, db):
    tasks = []
    for record in records:
        task = process_record(db, record)
        # print(task)
        tasks.append(task)
    await asyncio.gather(*tasks)


async def process_record(db, record):
    async with aiohttp.ClientSession() as session:
        async with session.get(record.url) as response:
            if response.status == 200:
                job_listing = await response.json()
                for job in job_listing['jobs']:
                    job_finder = Job_Finder(job['id'], job['title'], job['location']['name'],
                                            job['updated_at'], job['absolute_url'])
                    job_data = job_finder.data()
                    new_job = Job_Model(company_id=record.id, job_id=job_data['id'],
                                        title=job_data['title'], country='Country',
                                        state='State', city='City', is_remote=False,
                                        is_hybrid=False, is_onsite=True, salary_low=80000.00,
                                        salary_high=120000.00, keywords=['keyword1', 'keyword2'],
                                        updated_at=datetime.datetime.now(), url=job_data['url'])
                    db.merge(new_job)
