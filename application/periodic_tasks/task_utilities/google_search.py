import os
import requests
from typing import List, Dict, Union, Any, Optional


class GoogleSearch:
    @staticmethod
    def search(query: str, start_index: int = 1, num_results: int = 10) -> Optional[Dict[str, Any]]:
        """
        Search Google using the Custom Search API.

        Args:
            query: The search query.
            start_index: The starting index of the search results.
            num_results: The number of results to fetch.

        Returns:
            The search results in JSON format.
        """
        params = {
            'key': os.getenv('GOOGLE_SEARCH_API_KEY'),
            'cx': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
            'q': query,
            'start': start_index,
            'num': num_results,
        }

        try:
            response = requests.get(
                'https://www.googleapis.com/customsearch/v1', params=params)
            response.raise_for_status()
            search_results = response.json()
            return search_results
        except requests.exceptions.RequestException as err:
            # raise Exception(f"Google Search API error: {err}")
            print(f"Google Search API error: {err}")
