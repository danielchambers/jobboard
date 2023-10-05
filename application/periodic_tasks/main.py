import json
import redis
import logging
import asyncio
import aiohttp
import datetime
from celery import shared_task, current_task
from sqlalchemy import and_
from application.database import database_context
from application.models.jobs import Company
# from application.models.jobs import Job as Job_Model
from application.periodic_tasks.task_utilities.company_finder import CompanyFinder
from application.periodic_tasks.task_utilities.greenhouse import process_greenhouse
from application.periodic_tasks.task_utilities.lever import process_lever
from application.periodic_tasks.task_utilities.google_search import GoogleSearch

import requests
logging.basicConfig(level=logging.INFO)
redis_client = redis.Redis(host='redis', port=6379, db=1)


@shared_task
def collect_companies(job_platform, query_term, date_restrict):
    MAX_SERACH_RESULTS = 91
    PLATFORMS = {
        'greenhouse': {
            'search_query': 'site:boards.greenhouse.io',
            'url_pattern': r"boards\.greenhouse\.io\/(?P<company_name>\w+)",
            'url_format': 'https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true',
        },
        'lever': {
            'search_query': 'site:jobs.lever.co',
            'url_pattern': r"jobs\.lever\.co\/(?P<company_name>\w+)",
            'url_format': 'https://jobs.lever.co/v0/postings/{}/?mode=json',
        },
        'careerpuck': {
            'search_query': 'site:app.careerpuck.com/job-board/',
            'url_pattern': r"app\.careerpuck\.com\/job-board\/(?P<company_name>\w+)",
            'url_format': 'https://api.careerpuck.com/v1/public/job-boards/{}',
        },
        'ashbyhq': {
            'search_query': 'site:jobs.ashbyhq.com',
            'url_pattern': r"jobs\.ashbyhq\.com\/(?P<company_name>\w+)",
            'url_format': 'https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams',
        },
        'myworkdayjobs': {
            'search_query': 'site:myworkdayjobs.com',
            'url_pattern': r'(?P<company_name>\w+)\.(?P<company_region>\w+)\.myworkdayjobs\.com\/(?:[a-z]{2}-[A-Z]{2}\/)?(?P<company_uri>\w[\w\-]*|(?!.*\/)([^\/?#]+))',
            'url_format': 'https://{company_name}.{company_region}.myworkdayjobs.com/wday/cxs/{company_name}/{company_uri}/jobs',
        },
    }

    results = []
    page_index = 1
    page_results = 10  # higher than 10 gives status 400
    query = f'{PLATFORMS.get(job_platform).get("search_query")} {query_term}'

    while True:
        search_results = GoogleSearch.search(
            query, page_index, page_results, date_restrict)
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
        for company in companies:
            existing_company = db.query(Company).filter_by(
                name=company['name'], platform=job_platform).first()

            if company['name']:
                new_company = Company(
                    name=company['name'], url=company['url'], platform=job_platform)
                if not existing_company:
                    db.add(new_company)


@shared_task
def collect_jobs(job_platform):
    last_page = int(redis_client.get('last_page') or 1)
    page_size = 10
    offset = (last_page - 1) * page_size

    with database_context() as db:
        records = db.query(Company).filter(and_(
            Company.platform == job_platform,
            Company.is_active == True)
        ).offset(offset).limit(page_size).all()
        companies = [{'id': record.id, 'url': record.url}
                     for record in records]
        platforms = {
            'greenhouse': process_greenhouse,
            'lever': process_lever,
        }
        asyncio.run(platforms[job_platform](companies))

    if len(records) < page_size:
        last_page = 1
    else:
        last_page += 1
        current_task.apply_async(args=[job_platform], countdown=120)

    redis_client.set('last_page', last_page)
