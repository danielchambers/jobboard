import os
import re
import requests
from typing import Dict, Any, Optional


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
        'dateRestrict': 'm1'
    }

    try:
        response = requests.get(
            'https://www.googleapis.com/customsearch/v1', params=params)
        response.raise_for_status()
        search_results = response.json()
        return search_results
    except requests.exceptions.HTTPError as err:
        print(err.response.status_code)


def parse_company_name(job_board: str, link: str) -> Optional[str]:
    """
    Extract the company name from a job board link using regex patterns.

    :param job_board: The job board type (e.g., 'greenhouse', 'lever').
    :param link: The job board link.
    :return: The extracted company name or None if no match found.
    """
    patterns = {
        'greenhouse': r"boards\.greenhouse\.io\/(?P<company_name>\w+)",
        'lever': r"jobs\.lever\.co\/(?P<company_name>\w+)",
        'careerpuck': r"app\.careerpuck\.com\/job-board\/(?P<company_name>\w+)",
        'myworkdayjobs': r"(?P<company_name>\w+)\.(?P<company_region>\w+)\.myworkdayjobs\.com\/en-US\/(?P<company_uri>[\w\-]+)"
    }
    match = re.search(patterns[job_board], link)
    return_data = {}

    if job_board == 'greenhouse':
        return_data['name'] = match.group("company_name")
    elif job_board == 'lever':
        return_data['name'] = match.group("company_name")
    elif job_board == 'careerpuck':
        return_data['name'] = match.group("company_name")
    elif job_board == 'myworkdayjobs':
        return_data = {
            'name': match.group("company_name"),
            'region': match.group("company_region"),
            'uri': match.group("company_uri")
        }
    return return_data


def get_company_names(job_board: str, search_query: str) -> None:
    """
    Perform the main job board company parsing and writing process.

    :param job_board: The job board type (e.g., 'greenhouse', 'lever').
    :param search_query: The search query for Google Custom Search API.
    """
    num_results = 10
    start_index = 1
    company_names = set()

    while True:
        search_results = google_search(search_query, start_index, num_results)
        if 'nextPage' not in search_results['queries'].keys():
            break

        for item in search_results.get('items'):
            company = parse_company_name(job_board, item['link'])
            company_names.add(company['name'])

        start_index += num_results
    return company_names
