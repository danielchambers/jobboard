import re
import json
import time
import html
import aiohttp
import asyncio
from lxml import html
from datetime import datetime
from application.models.jobs import Job
from application.database import database_context

start_time = time.time()


class GreenhouseParser:
    def __init__(self, job_data) -> None:
        self.id = job_data['id']
        self.company = job_data['company']
        self.position = job_data['position']
        self.url = job_data['url']
        self.updated = job_data['updated']
        self.location = job_data['location']
        self.content = job_data['content']

    def parse_job_date(self):
        return datetime.strptime(self.updated, "%Y-%m-%dT%H:%M:%S%z")

    def parse_workplace(self):
        workplace_data = {'onsite': True, 'hybrid': False, 'remote': False}
        remote_keywords = ['remote', 'home office']
        hybrid_keywords = ['hybrid', 'flexible']

        if any(keyword in s.lower() for s in [self.position, self.location] for keyword in remote_keywords):
            workplace_data['onsite'] = False
            workplace_data['remote'] = True
        elif any(keyword in s.lower() for s in [self.position, self.location] for keyword in hybrid_keywords):
            workplace_data['onsite'] = False
            workplace_data['hybrid'] = True
        return workplace_data

    def state_abbreviation_to_name(self, state_abbreviation):
        state_abbreviation = state_abbreviation.strip().upper()
        state_abbreviations = {
            "AL": "Alabama",
            "AK": "Alaska",
            "AZ": "Arizona",
            "AR": "Arkansas",
            "CA": "California",
            "CO": "Colorado",
            "CT": "Connecticut",
            "DE": "Delaware",
            "FL": "Florida",
            "GA": "Georgia",
            "HI": "Hawaii",
            "ID": "Idaho",
            "IL": "Illinois",
            "IN": "Indiana",
            "IA": "Iowa",
            "KS": "Kansas",
            "KY": "Kentucky",
            "LA": "Louisiana",
            "ME": "Maine",
            "MD": "Maryland",
            "MA": "Massachusetts",
            "MI": "Michigan",
            "MN": "Minnesota",
            "MS": "Mississippi",
            "MO": "Missouri",
            "MT": "Montana",
            "NE": "Nebraska",
            "NV": "Nevada",
            "NH": "New Hampshire",
            "NJ": "New Jersey",
            "NM": "New Mexico",
            "NY": "New York",
            "NC": "North Carolina",
            "ND": "North Dakota",
            "OH": "Ohio",
            "OK": "Oklahoma",
            "OR": "Oregon",
            "PA": "Pennsylvania",
            "RI": "Rhode Island",
            "SC": "South Carolina",
            "SD": "South Dakota",
            "TN": "Tennessee",
            "TX": "Texas",
            "UT": "Utah",
            "VT": "Vermont",
            "VA": "Virginia",
            "WA": "Washington",
            "WV": "West Virginia",
            "WI": "Wisconsin",
            "WY": "Wyoming",
            "DC": "District of Columbia"
        }

        return state_abbreviations.get(state_abbreviation)

    def location_identifier(self, word):
        # Load the lists of cities, states, and countries from JSON files
        with open('application/periodic_tasks/task_utilities/city.json', 'r') as f:
            cities = json.load(f)

        with open('application/periodic_tasks/task_utilities/state.json', 'r') as f:
            states = json.load(f)

        with open('application/periodic_tasks/task_utilities/country.json', 'r') as f:
            countries = json.load(f)

        classification = ''
        if word in cities:
            classification = "city"
        elif word in states:
            classification = "state"
        elif word in countries:
            classification = "country"
        elif word in ['Remote', 'Onsite', 'Hybrid']:
            classification = "workplace"
        else:
            classification = "unknown"  # If the word is not found in any of the lists

        return classification

    def parse_location(self):
        # remove leading and trailing whitespace along with strings ending in , or .
        pre_clean_raw = self.location.strip().rstrip(',').rstrip('.')
        # print(pre_clean_raw)
        # edge cases
        change_edge_cases = pre_clean_raw.replace(
            'San Francisco Bay Area', 'San Francisco').replace('SF Bay Area', 'San Francisco').replace('LATAM', 'Latin America')
        # print(change_edge_cases)
        # change new york to new york city
        new_york_pattern = r'(New\sYork),\s(NY|New\sYork)'
        match_ny_pattern = re.search(new_york_pattern, change_edge_cases)
        if match_ny_pattern:
            change_edge_cases = re.sub(
                new_york_pattern, f'New York City, {match_ny_pattern.group(2)}', self.location)
        # change all United Staets instances to USA
        change_country = re.sub(
            r'United States|USA|US|\(US\)|\(USA\)|\(U\.S\.\)|\(U\.S\.A\.\)|U\.S\.A\.|U\.S\.', 'USA', change_edge_cases)
        # remove unnecessary words from (Remote) -> Remote and add commas before or after the word
        change_stop_words = re.sub(
            r'(?:\s(?:or|in|but|and|Based)\s|\b(?:or|in|but|and|Based)\b)', '', change_country)
        # print(change_stop_words)
        # change workplace keywords

        def replace(match):
            matched_word = match.group(0).replace('(', '').replace(')', '')
            if match.start() == 0:  # If it starts the string
                return matched_word.title() + ','
            elif match.end() == len(change_stop_words):  # If it ends the string
                return ',{}'.format(matched_word.title())
            else:
                return ',{},'.format(matched_word.title())

        result = re.sub(r'\((Remote|Hybrid|Onsite)\)|(Remote|Hybrid|Onsite)',
                        replace, change_stop_words, re.IGNORECASE)
        # clean extra commas
        change_commas = result.replace(',,', ', ').replace(', ,', ', ').replace(
            ' - ,', ', ').replace(', - ', ', ').replace('. ,', ', ').replace(', : ', ', ').rstrip(',').rstrip('.')
        # tokenize location string after all changes
        parts = re.split(r'[^\w\s]+', change_commas)
        clean_parts = [part.strip() for part in parts]
        # change state abbreviations
        state_abbreviations = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
            "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
            "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
            "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
        ]
        for i, item in enumerate(clean_parts):
            if item.upper() in state_abbreviations:
                clean_parts[i] = self.state_abbreviation_to_name(item.upper())

        # label each token
        clean_parts_label = [self.location_identifier(
            part.strip()) for part in clean_parts]
        # zip tokens and labels and return
        tokens_and_labels = zip(clean_parts, clean_parts_label)
        locations = {
            # 'raw': self.location,
            'state': set(),
            'city': set(),
            'country': set()
        }
        for item in tokens_and_labels:
            if item[1] == 'state':
                locations['state'].add(item[0])
            elif item[1] == 'city':
                locations['city'].add(item[0])
            elif item[1] == 'country':
                locations['country'].add(item[0])
        locations['state'] = list(locations['state'])
        locations['city'] = list(locations['city'])
        locations['country'] = list(locations['country'])
        return locations

    def parse_keywords(self):
        keywords = {'circleci', 'python', 'c#', 'azure', 'pulumi', 'sass', 'sqs', 'kotlin', 'terraform', 'leaflet',
                    'node', 'scratch', 'ec2', 'asp.net', 'rust', 'lisp', 'cartography', 'kafka', 'cassandra', 'ibm cloud',
                    'puppet', 'kubernetes', 'oracle cloud', 'ansible', 'angularjs', 'lua', 'ruby', 'nosql', 'elasticsearch',
                    'cockroachdb', 'typescript', 'php', 'haskell', 'svn', 'apis', 'geospatial', 'eks', 'objective-c', 'c++',
                    'github', 'java', 'rdbms', 'fortran', 'assembly', 'defi', 'jenkins', 'amazon web services', 'express',
                    'matlab', 'grafana', 'react', 'bitbucket', 'jupyter', 'excel', 'dart', 'nodejs', 'angular', 'kinesis',
                    'flink', 'vue', 'golang', 'flask', 'laravel', 'rest', 'perl', 'erlang', 'spring', 'gcp', 'gitlab',
                    'indexeddb', 'javascript', 'rails', 'elk', 'css', 'bamboo', 'datadog', 'spark', 'sqlalchemy', 'nfts',
                    'html', 's3', 'docker', 'mapreduce', 'elixir', 'deckgl', 'chef', 'cloudflare', 'mapbox', 'backbone',
                    '.net', 'go', 'julia', 'graphql federation', 'http', 'prolog', 'webgl', 'fastapi', 'ember', 'jquery',
                    'google cloud platform', 'big data', 'ecs', 'hadoop', 'postgresql', 'git', 'bash', 'mongodb', 'gis',
                    'swift', 'django', 'mercurial', 'travisci', 'dynamodb', 'mysql', 'sql', 'aws', 'scala', 'cobol',
                    'redis', 'redshift'}
        # words = [word.lower() for word in word_tokenize(text_response)]
        words = set()
        for token in re.split(r'[^a-zA-Z0-9]+', self.content.replace('\n', ' ')):
            w = token.lower().strip()
            if len(w) > 2:
                words.add(w)

        common_keywords = set(words).intersection(keywords)
        return list(common_keywords)

    def extract_pay_scale(self, pay_range, text_response):
        def get_search(text):
            pattern = r'\$(?P<lower>[\d,.kK]{2,})(\s(?:to|and|-|~|_|–|—)\s|(?:to|and|-|~|_|/|–|—))\$?(?P<upper>[\d,.kK]+)'
            return re.search(pattern, text, re.IGNORECASE)

        def process_price(text):
            return_data = {}
            remove_pattern = r'[^\w+]'
            match = get_search(text)
            if match:
                return_data['lower'] = re.sub(
                    remove_pattern, '', match.group('lower').lower().replace('.00', '').replace('k', ',000'))
                return_data['upper'] = re.sub(
                    remove_pattern, '', match.group('upper').lower().replace('.00', '').replace('k', ',000'))
            else:
                return_data['lower'] = 0
                return_data['upper'] = 0
            return return_data

        if pay_range:
            return process_price(pay_range.strip())
        else:
            return process_price(text_response.replace(' ', ''))

    def get_data(self):
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'url': self.url,
            'updated': self.parse_job_date(),
            'workplace': self.parse_workplace(),
            'location': self.parse_location(),
            'keywords': self.parse_keywords(),
            'payscale': {'low': 0, 'high': 0}
        }


async def greenhouse_http_request(session, company):
    async with session.get(company['url']) as resp:
        if resp.status == 404:
            return {'jobs': [], 'active_status': False}
        response = await resp.json()
        jobs = []
        for job in response['jobs']:
            job_data = {
                'id': job['id'],
                'company': company['id'],
                'position': job['title'],
                'url': job['absolute_url'],
                'location': job['location']['name'],
                'updated': job['updated_at'],
                'content': job['content']
            }
            jobs.append(job_data)
        return {'jobs': jobs, 'active_status': True}


async def process_greenhouse(companies):
    async with aiohttp.ClientSession() as session:
        company_data = [asyncio.ensure_future(
            greenhouse_http_request(session, company)) for company in companies]

        companies = await asyncio.gather(*company_data)

        available_jobs = []
        for company in companies:
            if company['active_status']:
                for job in company['jobs']:
                    greenhouse_job = GreenhouseParser(job)
                    available_jobs.append(greenhouse_job.get_data())

        save_jobs = []
        for job in available_jobs:
            new_job = Job(company_id=job['company'], job_id=job['id'], title=job['position'],
                          city=job['location']['city'], state=job['location']['state'], country=job['location']['country'],
                          is_remote=job['workplace']['remote'], is_hybrid=job['workplace']['hybrid'], is_onsite=job['workplace']['onsite'],
                          salary_low=job['payscale']['low'], salary_high=job['payscale']['high'], keywords=job['keywords'],
                          updated_at=job['updated'], url=job['url'])
            save_jobs.append(new_job)

        with database_context() as db:
            db.add_all(save_jobs)


# print("--- %s seconds ---" % (time.time() - start_time))
