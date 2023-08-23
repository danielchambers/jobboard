import redis
from celery import shared_task
from sqlalchemy.exc import IntegrityError
from application.database import database_context
from application.models.jobs import Company
from application.periodic_tasks.task_utilities.company_finder import CompanyFinder


@shared_task
def company_names(job_board, location, query):
    cf = CompanyFinder(job_board)
    companies = cf.search(f'{location} AND {query}')
    for company in companies:
        print(company)


# @shared_task
# def greenhouse_jobs():
#     redis_client = redis.Redis(host='redis', port=6379, db=2)
#     page_size = 10  # Adjust page size if needed
#     page_number = 1

#     if redis_client.exists('greenhouse_company_page_number'):
#         page_number = int(redis_client.get('greenhouse_company_page_number'))

#     with get_db() as db:
#         offset = (page_number - 1) * page_size
#         companies = db.query(Company).limit(
#             page_size).offset(offset).all()
#         redis_client.set('greenhouse_company_page_number', page_number + 1)

#     for company in companies:
#         logger.info(f"Fetching jobs for {company.identifier}")
#         listing = get_greenhouse_jobs(company.identifier)
#         jobs = listing['jobs']
#         total_jobs = listing['meta']['total']
#         logger.info(f"Total jobs: {total_jobs}")

#         if total_jobs > 0:
#             with get_db() as db:
#                 for job in jobs:
#                     new_job_data = parse_greenhouse_job(company.id, job)
#                     new_job = GreenhouseJob(**new_job_data)
#                     db.add(new_job)
#                 logger.info(
#                     f"Inserted {len(jobs)} jobs for {company.identifier}")
