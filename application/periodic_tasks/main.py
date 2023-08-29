import redis
from celery import shared_task
from sqlalchemy.exc import IntegrityError
from application.database import database_context
from application.models.jobs import Company
from application.periodic_tasks.task_utilities.company_finder import CompanyFinder
from application.periodic_tasks.task_utilities.google_search import GoogleSearch


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
    page_results = 10
    query = PLATFORMS.get(job_platform).get(
        'search_query').format(f'{location} AND {job_title}')

    while True:
        search_results = GoogleSearch.search(query, page_index, page_results)
        if page_index >= MAX_SERACH_RESULTS:
            break
        if search_results.get('items') is None:
            break
        items = search_results.get('items')
        links = [item['link'] for item in items if items]
        results.extend(links)
        page_index += page_results

    company_finder = CompanyFinder(job_platform, PLATFORMS.get(job_platform))
    companies = company_finder.parse(results)
    with database_context() as db:
        db.add_all([Company(**company) for company in companies])


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
