import redis
import logging
from contextlib import contextmanager
from celery import shared_task
from sqlalchemy.exc import IntegrityError
from application.database import SessionLocal
from .models import GreenhouseCompany, GreenhouseJob
from .models import LeverCompany
from .company_names import get_company_names
from .company_jobs import get_greenhouse_jobs, parse_greenhouse_job


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except IntegrityError:
        logger.warning("Integrity error occurred. Rolling back.")
        session.rollback()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        session.rollback()
        raise
    finally:
        session.close()


@shared_task
def company_names(job_board, state, query):
    states = {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        'AR': 'Arkansas',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'IA': 'Iowa',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'ME': 'Maine',
        'MD': 'Maryland',
        'MA': 'Massachusetts',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MS': 'Mississippi',
        'MO': 'Missouri',
        'MT': 'Montana',
        'NE': 'Nebraska',
        'NV': 'Nevada',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NY': 'New York',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VT': 'Vermont',
        'VA': 'Virginia',
        'WA': 'Washington',
        'WV': 'West Virginia',
        'WI': 'Wisconsin',
        'WY': 'Wyoming'
    }
    job_boards = {
        'greenhouse': 'boards.greenhouse.io',
        'lever': 'jobs.lever.co',
        'myworkdayjobs': 'myworkdayjobs.com/en-US/',
        'ashbyhq': 'jobs.ashbyhq.com',
        'careerpuck': 'app.careerpuck.com/job-board/',
        #
        'smartrecruiters': 'careers.smartrecruiters.com',
        'jobvite': 'jobs.jobvite.com'
    }
    search_query = f'site:{job_boards[job_board]} {states[state]} OR {state} AND {query}'
    names = get_company_names(job_board, search_query)

    if len(names) > 0:
        for name in names:
            new_company = {
                'greenhouse': GreenhouseCompany(identifier=name),
                'lever': LeverCompany(identifier=name)
            }

            with get_db() as db:
                db.add(new_company[job_board])
                db.commit()


@shared_task
def greenhouse_jobs():
    redis_client = redis.Redis(host='redis', port=6379, db=2)
    page_size = 10  # Adjust page size if needed
    page_number = 1

    if redis_client.exists('greenhouse_company_page_number'):
        page_number = int(redis_client.get('greenhouse_company_page_number'))

    with get_db() as db:
        offset = (page_number - 1) * page_size
        companies = db.query(GreenhouseCompany).limit(
            page_size).offset(offset).all()
        redis_client.set('greenhouse_company_page_number', page_number + 1)

    for company in companies:
        logger.info(f"Fetching jobs for {company.identifier}")
        listing = get_greenhouse_jobs(company.identifier)
        jobs = listing['jobs']
        total_jobs = listing['meta']['total']
        logger.info(f"Total jobs: {total_jobs}")

        if total_jobs > 0:
            with get_db() as db:
                for job in jobs:
                    new_job_data = parse_greenhouse_job(company.id, job)
                    new_job = GreenhouseJob(**new_job_data)
                    db.add(new_job)
                logger.info(
                    f"Inserted {len(jobs)} jobs for {company.identifier}")
