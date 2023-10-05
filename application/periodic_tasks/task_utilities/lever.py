import re
import json
import aiohttp
import asyncio
from datetime import datetime, timezone, timedelta
from application.database import database_context
from application.models.jobs import Job


class LeverParser:
    def __init__(self, job_data) -> None:
        self.id = job_data['id']
        self.company = job_data['company']
        self.position = job_data['position']
        self.url = job_data['url']
        self.updated = job_data['updated']
        self.location = job_data['location']
        self.workplace = job_data['workplace']
        self.payscale = job_data['payscale']
        self.content = job_data['content']

    def parse_workplace(self):
        return_data = {'onsite': False, 'remote': False, 'hybrid': False}
        replace_nonwords = re.sub(r'[\W]+', '', self.workplace).lower()
        if self.location.split('##')[-1] == 'US':
            if replace_nonwords == 'unspecified':
                def find_workplace(input_string):
                    keywords = ['onsite', 'remote',
                                'hybrid', 'inoffice', 'office']
                    tokens = re.split(
                        r'[^\w]+', input_string, flags=re.IGNORECASE)
                    for token in tokens:
                        if token.lower() in keywords:
                            return True, token.lower()
                    return False, None

                is_location, workplace_location = find_workplace(self.location)
                is_position, workplace_position = find_workplace(self.position)
                if is_location:
                    replace_nonwords = workplace_location
                elif is_position:
                    replace_nonwords = workplace_position
                else:
                    replace_nonwords = 'onsite'

        if replace_nonwords == 'hybrid':
            return_data['hybrid'] = True
            return_data['onsite'] = True
        elif replace_nonwords == 'remote':
            return_data['remote'] = True
        else:
            return_data['onsite'] = True
        return return_data

    def location_identifier(self, word):
        # Load the lists of cities, states, and countries from JSON files
        with open('application/periodic_tasks/task_utilities/city.json', 'r') as f:
            cities = json.load(f)

        with open('application/periodic_tasks/task_utilities/state.json', 'r') as f:
            states = json.load(f)

        with open('application/periodic_tasks/task_utilities/country.json', 'r') as f:
            countries = json.load(f)

        clean_word = word.strip()
        classification = ''
        if clean_word in cities:
            classification = "city"
        elif clean_word in states:
            classification = "state"
        elif clean_word in countries:
            classification = "country"
        elif clean_word.lower().replace('-', '').replace(' ', '') in ['remote', 'onsite', 'hybrid', 'inoffice']:
            classification = "workplace"
        else:
            classification = "unknown"  # If the clean_word is not found in any of the lists

        return classification

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

    def country_abbreviation_to_name(self, country_abbreviation):
        country_abbreviation = country_abbreviation.strip().upper()
        country_abbreviations = {
            'AF': 'Afghanistan',
            'AL': 'Albania',
            'DZ': 'Algeria',
            'AD': 'Andorra',
            'AO': 'Angola',
            'AG': 'Antigua and Barbuda',
            'AR': 'Argentina',
            'AM': 'Armenia',
            'AU': 'Australia',
            'AT': 'Austria',
            'AZ': 'Azerbaijan',
            'BS': 'Bahamas',
            'BH': 'Bahrain',
            'BD': 'Bangladesh',
            'BB': 'Barbados',
            'BY': 'Belarus',
            'BE': 'Belgium',
            'BZ': 'Belize',
            'BJ': 'Benin',
            'BT': 'Bhutan',
            'BO': 'Bolivia',
            'BA': 'Bosnia and Herzegovina',
            'BW': 'Botswana',
            'BR': 'Brazil',
            'BN': 'Brunei',
            'BG': 'Bulgaria',
            'BF': 'Burkina Faso',
            'BI': 'Burundi',
            'CV': 'Cabo Verde',
            'KH': 'Cambodia',
            'CM': 'Cameroon',
            'CA': 'Canada',
            'CF': 'Central African Republic',
            'TD': 'Chad',
            'CL': 'Chile',
            'CN': 'China',
            'CO': 'Colombia',
            'KM': 'Comoros',
            'CG': 'Congo',
            'CD': 'Democratic Republic of the Congo',
            'CR': 'Costa Rica',
            'HR': 'Croatia',
            'CU': 'Cuba',
            'CY': 'Cyprus',
            'CZ': 'Czech Republic',
            'CI': "Côte d'Ivoire (Ivory Coast)",
            'DK': 'Denmark',
            'DJ': 'Djibouti',
            'DM': 'Dominica',
            'DO': 'Dominican Republic',
            'EC': 'Ecuador',
            'EG': 'Egypt',
            'SV': 'El Salvador',
            'GQ': 'Equatorial Guinea',
            'ER': 'Eritrea',
            'EE': 'Estonia',
            'ET': 'Ethiopia',
            'FJ': 'Fiji',
            'FI': 'Finland',
            'FR': 'France',
            'GA': 'Gabon',
            'GM': 'Gambia',
            'GE': 'Georgia',
            'DE': 'Germany',
            'GH': 'Ghana',
            'GR': 'Greece',
            'GD': 'Grenada',
            'GT': 'Guatemala',
            'GN': 'Guinea',
            'GW': 'Guinea-Bissau',
            'GY': 'Guyana',
            'HT': 'Haiti',
            'HN': 'Honduras',
            'HU': 'Hungary',
            'IS': 'Iceland',
            'IN': 'India',
            'ID': 'Indonesia',
            'IR': 'Iran',
            'IQ': 'Iraq',
            'IE': 'Ireland',
            'IL': 'Israel',
            'IT': 'Italy',
            'JM': 'Jamaica',
            'JP': 'Japan',
            'JO': 'Jordan',
            'KZ': 'Kazakhstan',
            'KE': 'Kenya',
            'KI': 'Kiribati',
            'KW': 'Kuwait',
            'KG': 'Kyrgyzstan',
            'LA': 'Laos',
            'LV': 'Latvia',
            'LB': 'Lebanon',
            'LS': 'Lesotho',
            'LR': 'Liberia',
            'LY': 'Libya',
            'LI': 'Liechtenstein',
            'LT': 'Lithuania',
            'LU': 'Luxembourg',
            'MK': 'North Macedonia',
            'MG': 'Madagascar',
            'MW': 'Malawi',
            'MY': 'Malaysia',
            'MV': 'Maldives',
            'ML': 'Mali',
            'MT': 'Malta',
            'MH': 'Marshall Islands',
            'MR': 'Mauritania',
            'MU': 'Mauritius',
            'MX': 'Mexico',
            'FM': 'Micronesia',
            'MD': 'Moldova',
            'MC': 'Monaco',
            'MN': 'Mongolia',
            'ME': 'Montenegro',
            'MA': 'Morocco',
            'MZ': 'Mozambique',
            'MM': 'Myanmar (Burma)',
            'NA': 'Namibia',
            'NR': 'Nauru',
            'NP': 'Nepal',
            'NL': 'Netherlands',
            'NZ': 'New Zealand',
            'NI': 'Nicaragua',
            'NE': 'Niger',
            'NG': 'Nigeria',
            'KP': 'North Korea',
            'NO': 'Norway',
            'OM': 'Oman',
            'PK': 'Pakistan',
            'PW': 'Palau',
            'PS': 'Palestine State',
            'PA': 'Panama',
            'PG': 'Papua New Guinea',
            'PY': 'Paraguay',
            'PE': 'Peru',
            'PH': 'Philippines',
            'PL': 'Poland',
            'PT': 'Portugal',
            'QA': 'Qatar',
            'RO': 'Romania',
            'RU': 'Russia',
            'RW': 'Rwanda',
            'KN': 'Saint Kitts and Nevis',
            'LC': 'Saint Lucia',
            'VC': 'Saint Vincent and the Grenadines',
            'WS': 'Samoa',
            'SM': 'San Marino',
            'ST': 'Sao Tome and Principe',
            'SA': 'Saudi Arabia',
            'SN': 'Senegal',
            'RS': 'Serbia',
            'SC': 'Seychelles',
            'SL': 'Sierra Leone',
            'SG': 'Singapore',
            'SK': 'Slovakia',
            'SI': 'Slovenia',
            'SB': 'Solomon Islands',
            'SO': 'Somalia',
            'ZA': 'South Africa',
            'KR': 'South Korea',
            'SS': 'South Sudan',
            'ES': 'Spain',
            'LK': 'Sri Lanka',
            'SD': 'Sudan',
            'SR': 'Suriname',
            'SZ': 'Swaziland',
            'SE': 'Sweden',
            'CH': 'Switzerland',
            'SY': 'Syria',
            'TW': 'Taiwan',
            'TJ': 'Tajikistan',
            'TZ': 'Tanzania',
            'TH': 'Thailand',
            'TL': 'Timor-Leste',
            'TG': 'Togo',
            'TO': 'Tonga',
            'TT': 'Trinidad and Tobago',
            'TN': 'Tunisia',
            'TR': 'Turkey',
            'TM': 'Turkmenistan',
            'TV': 'Tuvalu',
            'UG': 'Uganda',
            'UA': 'Ukraine',
            'AE': 'United Arab Emirates',
            'GB': 'United Kingdom',
            'US': 'United States',
            'UY': 'Uruguay',
            'UZ': 'Uzbekistan',
            'VU': 'Vanuatu',
            'VA': 'Vatican City (Holy See)',
            'VE': 'Venezuela',
            'VN': 'Vietnam',
            'YE': 'Yemen',
            'ZM': 'Zambia',
            'ZW': 'Zimbabwe'
        }

        return country_abbreviations.get(country_abbreviation)

    def tokenize_remote_string(self, input_string):
        return_data = []
        if 'remote' in input_string.lower():
            tokens = re.split(
                r'\b(?:and|or|\s\()\b', input_string, flags=re.IGNORECASE)
            for token in tokens:
                return_data.append(token.replace(')', '').strip())
        else:
            return_data.append(input_string)
        return return_data

    def token_classifier(self, raw_tokens):
        return_data = {'state': set(), 'city': set(), 'country': {'US'}}

        # remove emprty strings
        tokens = [token.strip() for token in raw_tokens if token]
        # convert state abbriviations
        new_tokens = []
        for token in tokens:
            if re.match(r'^[A-Z]{2}$', token):
                state = self.state_abbreviation_to_name(token)
                if state:
                    new_tokens.append(state)
            else:
                new_tokens.append(token)

        for token in new_tokens:
            location_type = self.location_identifier(token)

            if location_type == 'city':
                return_data['city'].add(token)
            elif location_type == 'state':
                return_data['state'].add(token)
            else:
                # TODO: send string to log for later parsing
                pass

        return_data['state'] = list(return_data['state'])
        return_data['city'] = list(return_data['city'])
        return_data['country'] = list(return_data['country'])

        return return_data

    def parse_location(self):
        return_data = {}
        location_tokens = self.location.split('##')
        if location_tokens[-1] == 'US':
            location_string = location_tokens[0]

            # removes: aaabbbccc ,83734 and aaabbbccc  (...)
            location_string = re.sub(
                r',?\s?(?:[0-9]{5}|\(.*\))$', '', location_string).strip()
            # remove trailing char: ,./;']=-[
            location_string = re.sub(
                r'\W?$', '', location_string).strip()
            # replace D.C. and D.C to DC
            dc_replace = re.search(
                r'Washington\W*(?P<district>(?:D\.C\.|D\.C))', location_string, flags=re.IGNORECASE)
            if dc_replace:
                location_string = re.sub(dc_replace.group(
                    'district'), 'DC', location_string, flags=re.IGNORECASE).strip()
            # remove * area (bay area, metro area)
            location_string = re.sub(
                r'\s(?:bay|metro)\sarea$', '', location_string, flags=re.IGNORECASE).strip()
            # remove trailing char and remote
            # Los Angeles, CA; Remote
            # Palo Alto, CA/Remote
            # Palo Alto, CA  / Remote
            location_string = re.sub(
                r'((?:;\s?|\/\s?|:\s?)Remote)$', '', location_string, flags=re.IGNORECASE).strip()
            # Rename St. and Ft.
            location_string = location_string.replace('Ft.', 'Ft')
            location_string = location_string.replace('St.', 'St')
            # Navy Yard
            location_string = location_string.replace(
                'Navy Yard', '').strip()
            # san fran
            location_string = location_string.replace(
                'San Francisco Bay Area', 'San Francisco')
            location_string = location_string.replace(
                'Bay Area', 'San Francisco')
            # New York
            location_string = location_string.replace("NYC", "New York City")
            location_string = location_string.replace(
                "New York Metropolitan Area", "New York City")
            # remove area from tail of string
            location_string = re.sub(
                r'\bArea$', '', location_string, flags=re.IGNORECASE).strip()
            # Remove "Greater" at the beginning of string
            location_string = re.sub(
                r'^Greater\s\w+', '', location_string, flags=re.IGNORECASE).strip()

            match_city_state = re.search(
                r'^(?P<city>[A-Za-z.\s]+),\s?(?P<state>[A-Z]{2})$', location_string)
            match_city_state_country = re.search(
                r'^(?P<city>[^,]+),\s(?P<state>(?:[A-Z]{2}|[A-Za-z\s]+)),\s(?:United\sStates|USA|US)$', location_string)
            match_remote_state = re.search(
                r'^Remote[\W\s]+(?!US)(?P<state>[A-Z]{2})$', location_string, flags=re.IGNORECASE)
            match_multiple_city_state_slash = re.search(
                r'^(\b[a-zA-Z.-]+\s\w+|\w+\b),\s?([A-Z]{2})(?:\s?(?:\/|or|and|\&|\;)\s?(\b[a-zA-Z.-]+\s\w+|\w+\b)[^\w]+([A-Z]{2}))*$(?!.*\b[A-Z]{2}\b)', location_string)
            match_united_states_location = re.search(
                r'^United\sStates\s*-\s*(?P<location>[A-Za-z\s]+)$', location_string, flags=re.IGNORECASE)
            match_state_city = re.search(
                r'^(?P<location1>[A-Za-z\s]+)\s*\-\s*(?P<location2>[A-Za-z\s]+)$', location_string, flags=re.IGNORECASE)
            match_city_state_united_staes = re.search(
                r'^(?P<location1>[A-Za-z\s]+)\s?-\s?(?P<location2>[A-Za-z\s]+)\s?-\s?United\sStates$', location_string)

            if match_city_state:
                # Los Angeles, CA
                # West Palm Beach, FL
                # Chicago, IL
                # Chicago,IL
                return_data['city'] = [match_city_state.group('city')]
                return_data['state'] = [self.state_abbreviation_to_name(
                    match_city_state.group('state'))]
                return_data['country'] = ['US']
            elif match_city_state_country:
                # Los Angeles, California, US
                # Chicago, Illinoes, United States
                # Los Angeles, California, United States
                # West Palm Beach, Florida, United States
                # Chicago, IL, United States
                # Los Angeles, CA, United States
                # West Palm Beach, FL, United States
                return_data['city'] = [match_city_state_country.group('city')]
                if match_city_state_country.group('state').isupper() and len(match_city_state_country.group('state')) == 2:
                    return_data['state'] = [self.state_abbreviation_to_name(
                        match_city_state_country.group('state'))]
                else:
                    return_data['state'] = [
                        match_city_state_country.group('state')]
                return_data['country'] = ['US']
            elif match_remote_state:
                # Remote- TN
                # Remote- WA
                # Remote - WA
                # Remote -WA
                # Remote-WA
                tokens = match_remote_state.group('state')
                return_data = self.token_classifier([tokens])
                # print(f"%%%%%%%{return_data}")
            elif match_multiple_city_state_slash:
                # San Francisco, CA & Pittsburgh, PA
                # San Francisco, CA / Reston, VA
                # San Francisco, CA & Reston, VA
                # San Francisco, CA; Remote US; Pittsburgh, PA
                # San Francisco, CA; Remote US ; Pittsburgh, PA
                # San Francisco, CA & Fort Worth, TX
                # Reston, VA or Washington, DC
                # Costa Mesa, CA or Boston, MA or Seattle, WA
                # Costa Mesa, CA / Quincy, MA / Boston, MA
                # Raleigh, NC; Durham, NC
                clean_str = re.sub(
                    r'(?:[^\w]+Remote\s*US$|\sRemote\sUS\s?\W)', '', location_string)
                tokens = re.split(r'\b\s*(?:;|&|\/|or|and)\s*\b', clean_str)
                flattened_data = []
                for token in tokens:
                    parts = token.split(",")
                    flattened_data.extend(parts)
                return_data = self.token_classifier(flattened_data)
                # print(f"%%%%%%%{return_data}")
            elif re.search(r'^(\w+(?: \w+)*)((?:\s*\/\s*\w+(?: \w+)*))+$', location_string, flags=re.IGNORECASE):
                # Los Angeles / San Francisco / San Diego
                tokens = re.split(r'\s*\/\s*', location_string)
                return_data = self.token_classifier(tokens)
                # print(f"%%%%%%%{return_data}")
            elif re.search(r'^([A-Za-z\s\-]+)\s*,\s*([A-Za-z\s\-]+)$', location_string):
                # El Segundo, California
                # Mojave, California
                # Denver, Colorado
                # San Francisco, California
                # Santa Monica, Los Angeles
                # California, United States
                # North Carolina, United States
                tokens = re.split(r'\s*,\s*', location_string)
                if tokens[0].lower() == 'new york' and tokens[1].lower() == 'new york':
                    tokens[1] = 'New York City'
                return_data = self.token_classifier(tokens)
                # print(f"%%%%%%%{return_data}")
            elif match_united_states_location:
                # United States - San Antonio
                # United States - Atlanta
                # United States - Seattle
                tokens = match_united_states_location.group('location')
                return_data = self.token_classifier([tokens])
                # print(f"%%%%%%%{return_data}")
            elif match_state_city:
                # Massachusetts - Boston
                # Missouri - Kansas City
                # Pennsylvania - Philadelphia
                # Ohio - Columbus
                tokens = [
                    match_state_city.group('location1'),
                    match_state_city.group('location2')
                ]
                if tokens[0].lower() == 'new york' and tokens[1].lower() == 'new york':
                    tokens[1] = 'New York City'
                return_data = self.token_classifier(tokens)
                # print(f"%%%%%%%{return_data}")
            elif re.search(r'^(?P<timezone>.+)\s((?:[T|t]ime)|(?:T|t)ime\s(?:Z|z)ones?)\s\(.+\)$', location_string):
                # Eastern US time zone (remote)
                # Central Time Zone (remote)
                # Central and Eastern US Time Zones (remote)
                # Eastern Time (US or Canada)
                return_data['state'] = []
                return_data['city'] = []
                return_data['country'] = ['US']
            elif re.search(r'^(?=.*\sor\s\w).+$', location_string):
                # San Francisco or New York City
                # Remote or In Office
                # New York City or Remote
                # Toronto or San Francisco or Remote
                # New York City or Los Angeles
                # Paris or America
                tokens = re.split(r'\sor\s', location_string)
                return_data = self.token_classifier(tokens)
                # print(f"%%%%%%%{return_data}")
            elif re.search(r'^(?:[A-Z]{2},\s*)+[A-Z]{2}$', location_string):
                # CA, TX, FL, AZ, NY
                tokens = location_string.split(',')
                return_data = self.token_classifier(tokens)
                # print(f"%%%%%%%{return_data}")
            elif match_city_state_united_staes:
                # Jacksonville - Florida - United States
                # Los Angeles - California - United States
                tokens = [
                    match_city_state_united_staes.group('location1'),
                    match_city_state_united_staes.group('location2')
                ]
                return_data = self.token_classifier(tokens)
                # print(f"%%%%%%%{return_data}")
            else:
                # remove beginning string USA, US, Remote
                location_string = re.sub(
                    r'^(?:US|USA|Remote),?\s', '', location_string, flags=re.IGNORECASE)

                if re.search(r'[^A-Za-z\s]+', location_string):
                    tokens = re.split(r'[^A-Za-z\s]+', location_string)
                    return_data = self.token_classifier(tokens)
                    # print(f"%%%%%%%{return_data}")
                else:
                    tokens = [location_string]
                    return_data = self.token_classifier(tokens)
                    # print(f"%%%%%%%{return_data}")
        else:
            return_data['country'] = [location_tokens[-1]]
        # non US postings
        return return_data

    def parse_keywords(self):
        keywords = {'ibm cloud', 'oracle cloud', 'amazon web services', 'decentralized finance',
                    'amazon elastic compute', 'apache spark', 'nonfungible tokens', 'non-fungible tokens',
                    'google cloud platform', 'big data', 'amazon ecs', 'elastic container service',
                    'graphql federation', 'version control system', 'version control', 'shell scripting',
                    'travis ci', 'amazon dynamodb', 'amazon s3', '.net', 'angular', 'angularjs', 'angular.js', 'angular js', 'ansible',
                    'apis', 'asp.net', 'assembly', 'aws', 'azure', 'backbone', 'backbone.js', 'backbone js', 'backbonejs', 'bamboo',
                    'bash', 'bitbucket', 'c#', 'c++', 'cartography', 'cassandra', 'chef', 'ci/cd', 'ci cd', 'cicd', 'circleci',
                    'cloudflare', 'cobol', 'cockroachdb', 'cockroach db', 'crypto', 'cryptocurrency', 'css', 'dart',
                    'datadog', 'deck.gl', 'deckgl', 'defi', 'django', 'docker', 'dynamodb', 'dynamo db', 'ec2',
                    'ecs', 'eks', 'elasticsearch', 'elastic search', 'elixir', 'elk', 'emberjs', 'ember', 'ember.js', 'ember js', 'erlang',
                    'excel', 'express', 'express.js', 'express js', 'expressjs', 'fastapi', 'flask', 'flink', 'fortran', 'gcp', 'geospatial',
                    'gis', 'git', 'github', 'gitlab', 'go', 'golang', 'grafana', 'hadoop', 'haskell',
                    'html', 'http', 'indexeddb', 'indexed db', 'java', 'javascript', 'java script', 'jenkins', 'jquery', 'julia',
                    'jupyter', 'kafka', 'kibana', 'kinesis', 'kotlin', 'kubernetes', 'laravel', 'leaflet',
                    'lisp', 'logstash', 'lua', 'mapbox', 'mapreduce', 'matlab', 'mercurial', 'mongodb', 'mongo db',
                    'mongo', 'mysql', 'nfts', 'node', 'node.js', 'nodejs', 'node js', 'nosql', 'objective-c', 'perl', 'php',
                    'postgresql', 'prolog', 'pulumi', 'puppet', 'python', 'rails', 'rdbms', 'react', 'redis',
                    'redshift', 'rest', 'ruby', 'rust', 's3', 'sass', 'scala', 'scratch', 'spark', 'spring',
                    'sql', 'sqlalchemy', 'sqs', 'subversion', 'svn', 'swift', 'terraform', 'travisci',
                    'typescript', 'vue', 'vue.js', 'vuejs', 'vue js', 'webgl', 'snowflake', 'pytorch', 'tensorflow', 'llm', 'llms',
                    'cosmosdb', 'cosmos db', 'cosmos', 'sockets', 'websockets', 'web sockets', 'websocket', 'web socket', 'celery', 'machine learning',
                    'machine-learning', 'machine-learning', 'numpy', 'webscraping', 'web scraping', 'web-scraping', 'rabbitmq', 'rabbit mq', 'huey',
                    'dramatiq', 'unix', 'linux', 'pyramid', 'jinja', 'jinja2', 'webhooks', 'web hooks', 'twilio', 'stripe', 'slack', 'sqlite', 'peewee',
                    'djangoorm', 'django orm', 'ponyorm', 'pony orm', 'no sql', 'apache cassandra', 'apache', 'neo4j', 'neo 4j', 'pandas', 'scipy', 'd3.js',
                    'd3js', 'd3 js', 'matplotlib', 'matplot lib', 'markdown', 'mark down', 'nginx', 'wsgi', 'wsgi server', 'wsgi servers', 'gunicorn',
                    'mod_wsgi', 'modwsgi', 'mod wsgi', 'serverless', 'firebase', 'aws lambda', 'azure functions', 'gocd', 'cdci', 'cd/ci', 'cd ci',
                    'google cloud functions'}
        found_keywords = set()
        for keyword in keywords:
            pattern = re.compile(r'\b{}\b'.format(
                re.escape(keyword)), re.IGNORECASE)
            matches = pattern.findall(self.content.replace('\n', ' '))
            if matches:
                found_keywords.add(keyword)

        return list(found_keywords)

    def parse_payscale(self):
        pay_data = self.payscale
        if not pay_data:
            return None
        return pay_data

    def parse_updated(self):
        return datetime.fromtimestamp(self.updated / 1000.0, tz=timezone.utc)

    def get_data(self):
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'url': self.url,
            'updated': self.updated,
            'workplace': self.parse_workplace(),
            'location': self.parse_location(),
            'keywords': self.parse_keywords(),
            'payscale': self.parse_payscale()
        }


async def lever_http_request(session, company):
    async with session.get(company['url']) as resp:
        if resp.status == 404:
            return {'jobs': [], 'active_status': False}
        response = await resp.json()
        jobs = []
        for job in response:
            job_data = {}
            job_data['id'] = job['id']
            job_data['company'] = company['id']
            job_data['position'] = job['text']
            job_data['url'] = job['hostedUrl']
            job_data['location'] = f"{job.get('categories', '').get('location', '')}##{job['country']}"
            job_data['workplace'] = job['workplaceType']
            job_data['updated'] = job['createdAt']
            job_data['payscale'] = job.get('salaryRange', None)
            job_data['content'] = f'{job.get("descriptionPlain", "")} {job.get("additionalPlain", "")} {" ".join([section["content"] for section in job.get("lists", [])])}'
            jobs.append(job_data)
        return {'jobs': jobs, 'active_status': True}


async def process_lever(companies):
    async with aiohttp.ClientSession() as session:
        company_data = [asyncio.ensure_future(
            lever_http_request(session, company)) for company in companies]

        companies = await asyncio.gather(*company_data)

        available_jobs = []
        for company in companies:
            if company['active_status']:
                for job in company['jobs']:
                    if job['location'].split('##')[-1] == 'US':
                        available_jobs.append(job)

        for job in available_jobs:
            lever_job = LeverParser(job)
            job_data = lever_job.get_data()

            with database_context() as db:
                existing_job = db.query(Job).filter(
                    Job.job_id == job_data['id']).first()

                if not existing_job:
                    new_job = Job(
                        company_id=job_data['company'],
                        job_id=job_data['id'],
                        title=job_data['position'],
                        country=job_data['location']['country'],
                        state=job_data['location']['state'],
                        city=job_data['location']['city'],
                        is_remote=job_data['workplace']['remote'],
                        is_hybrid=job_data['workplace']['hybrid'],
                        is_onsite=job_data['workplace']['onsite'],
                        salary=job_data['payscale'],
                        keywords=job_data['keywords'],
                        updated_at=job_data['updated'],
                        url=job_data['url']
                    )
                    db.add(new_job)
