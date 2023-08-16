import random
from contextlib import contextmanager
from celery import shared_task
from sqlalchemy.exc import IntegrityError
from application.database import SessionLocal
from .models import GreenhouseCompany
from .models import LeverCompany
from .company_finder import company_names


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    except IntegrityError:
        # already exists
        session.rollback()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@shared_task
def get_company_names(job_board, state, query):
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
    names = company_names(job_board, search_query)

    if len(names) > 0:
        for name in names:
            new_company = {
                'greenhouse': GreenhouseCompany(identifier=name),
                'lever': LeverCompany(identifier=name)
            }

            with get_db() as db:
                db.add(new_company[job_board])
                db.commit()
