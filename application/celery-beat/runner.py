from contextlib import contextmanager
from database import Session
from models import GreenhouseCompany
from tasks.company_scraper import companies


@contextmanager
def get_db():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
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
    keywords = [
        'python',
        'javascript',
        'full-stack',
        'fullstack',
        'full stack',
        'react',
        'react developer',
        'backend',
        'backend developer',
        'backend engineer',
        'frontend',
        'frontend developer',
        'frontend engineer',
        'senior engineer',
        'senior software engineer',
        'software developer',
        'software developer i',
        'software developer ii',
        'software engineer',
        'software engineer i',
        'software engineer ii',
        'software',
        'entry level frontend',
        'entry level backend',
        'entry level fullstack',
        'entry level developer',
        'entry level engineer',
        'junior frontend',
        'junior backend',
        'junior fullstack',
        'junior developer',
        'junior engineer',
        'programmer'
    ]

    state = 'CA'
    job_board = 'lever'

    # for keyword in keywords:
    # print(os.getenv('DATABASE_URL'))
    search_query = f'site:{job_boards[job_board]} {states[state]} OR {state} AND fullstack developer'
    company_names = companies(job_board, search_query)
    if len(company_names) > 0:
        for name in company_names:
            # Insert data into the table using the context manager
            new_company_data = {'name': name, 'jobs_available': 0}
            with get_db() as db:
                new_company = GreenhouseCompany(**new_company_data)
                db.add(new_company)
