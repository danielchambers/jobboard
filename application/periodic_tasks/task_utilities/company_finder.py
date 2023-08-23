import os
import re
import requests
from typing import List, Dict, Union, Any, Optional


def google_search(query: str, start_index: int = 1, num_results: int = 10) -> Optional[Dict[str, Any]]:
    """
    Perform a Google Custom Search API request and return the search results.

    :param query: The search query.
    :param start_index: The index of the first result to retrieve. Default is 1.
    :param num_results: The number of results to retrieve. Default is 10.
    :return: The search results as a dictionary or None if there was an error.
    """
    params = {
        'key': os.getenv('GOOGLE_SEARCH_API_KEY'),
        'cx': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
        'q': query,
        'start': start_index,
        'num': num_results,
        # 'dateRestrict': 'm6'
    }

    try:
        response = requests.get(
            'https://www.googleapis.com/customsearch/v1', params=params)
        response.raise_for_status()
        search_results = response.json()
        return search_results
    except requests.exceptions.HTTPError as err:
        print(err.response.status_code)


class CompanyFinder:
    """
    A class for finding job listings from various company job boards.

    Attributes:
        job_board (str): The job board platform to search on.
        unique_companies (set): A set to store unique company names.
        companies (list): A list to store company information.
    """

    def __init__(self, job_board: str) -> None:
        """
        Initialize the CompanyFinder.

        Args:
            job_board (str): The job board platform to search on.
        """
        self.job_board = job_board
        self.unique_companies = set()
        self.companies = []

    def search(self, search_query: str) -> List[Dict[str, Union[str, str]]]:
        """
        Search for companies based on the provided search query.

        Args:
            search_query (str): The query to search for.

        Returns:
            List[Dict[str, Union[str, str]]]: A list of dictionaries containing company information.
        """
        page_index = 1
        page_results = 10
        full_search_query = {
            'greenhouse': f'site:boards.greenhouse.io {search_query}',
            'lever': f'site:jobs.lever.co {search_query}',
            'careerpuck': f'site:app.careerpuck.com/job-board/ {search_query}',
            'ashbyhq': f'site:jobs.ashbyhq.com {search_query}',
            'myworkdayjobs': f'site: myworkdayjobs.com {search_query}'
        }
        url_pattern = {
            'greenhouse': r"boards\.greenhouse\.io\/(?P<company_name>\w+)",
            'lever': r"jobs\.lever\.co\/(?P<company_name>\w+)",
            'careerpuck': r"app\.careerpuck\.com\/job-board\/(?P<company_name>\w+)",
            'ashbyhq': r"jobs\.ashbyhq\.com\/(?P<company_name>\w+)",
            'myworkdayjobs': r'(?P<company_name>\w+)\.(?P<company_region>\w+)\.myworkdayjobs\.com\/(?:[a-z]{2}-[A-Z]{2}\/)?(?P<company_uri>\w[\w\-]*|(?!.*\/)([^\/?#]+))'
        }
        while True:
            search_results = google_search(
                full_search_query[self.job_board], page_index, page_results)
            if search_results is None:
                break
            if 'nextPage' not in search_results['queries'].keys():
                break
            for item in search_results.get('items'):
                match = re.search(
                    url_pattern[self.job_board], item['link'])
                if self.job_board == "myworkdayjobs":
                    self.get_myworkdayjob(match)
                else:
                    self.get_company(match)
            page_index += page_results
        return self.companies

    def get_company(self, match: re.Match) -> None:
        """
        Extract and store company information from the provided match.

        Args:
            match (re.Match): The regular expression match object.
        """
        if match:
            company_name = match.group("company_name")
            url = {
                'greenhouse': f'https://boards-api.greenhouse.io/v1/boards/{company_name}/jobs/',
                'lever': f'https://jobs.lever.co/v0/postings/{company_name}?mode=json',
                'careerpuck': f'https://api.careerpuck.com/v1/public/job-boards/{company_name}',
                'ashbyhq': 'https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams'
            }
            if company_name not in self.unique_companies:
                self.companies.append({
                    'name': company_name,
                    'url': url[self.job_board],
                    'platform': self.job_board
                })
            self.unique_companies.add(company_name)

    def get_myworkdayjob(self, match: re.Match) -> None:
        """
        Extract and store myworkdayjobs company information from the provided match.

        Args:
            match (re.Match): The regular expression match object.
        """
        if match:
            company_name = match.group("company_name")
            if company_name not in self.unique_companies:
                company_location = match.group("company_region")
                company_uri = match.group("company_uri")
                json_url = f'https://{company_name}.{company_location}.myworkdayjobs.com/wday/cxs/{company_name}/{company_uri}/jobs'
                self.companies.append(
                    {'name': company_name, 'url': json_url, 'platform': self.job_board})
            self.unique_companies.add(company_name)
