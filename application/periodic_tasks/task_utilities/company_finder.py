import os
import re
from typing import List, Dict, Union, Any, Optional


class CompanyFinder:
    """
    Find company information from job links on various platforms.
    """

    def __init__(self, platform: str, platform_config: Dict[str, Dict[str, str]]) -> None:
        """
        Initialize the CompanyFinder instance.

        Args:
            platform: The selected job board.
            platform_config: The configuration for the selected platform.
        """
        self.platform = platform
        self.platform_config = platform_config
        self.unique_companies = set()
        self.companies = []

    def parse(self, links: List[str]) -> List[Dict[str, Union[str, str]]]:
        """
        Parse job links to extract company information.

        Args:
            links: List of job links.

        Returns:
            List of parsed company information.
        """
        if not self.platform_config:
            raise ValueError(f"Invalid job board: {self.platform}")

        for link in links:
            match = re.search(self.platform_config['url_pattern'], link)
            if match:
                if self.platform == "myworkdayjobs":
                    self._process_myworkdayjob_match(match)
                else:
                    self._process_company_match(
                        match, self.platform_config['url_format'])
        return self.companies

    def _process_company_match(self, match: re.Match, url_format: str) -> None:
        """
        Extract company information from a job link.

        Args:
            match: A regular expression match object.
            url_format: URL format for the company's API endpoint.
        """
        try:
            company_name = match.group("company_name")
            if company_name not in self.unique_companies:
                company_url = url_format.format(company_name)
                self.companies.append({
                    'name': company_name,
                    'url': company_url,
                    'platform': self.platform
                })
                self.unique_companies.add(company_name)
        except (AttributeError, IndexError, re.error) as err:
            print(f"Error processing link: {err}")

    def _process_myworkdayjob_match(self, match: re.Match) -> None:
        """
        Extract company information from a MyWorkDayJobs link.

        Args:
            match: A regular expression match object.
        """
        try:
            if match:
                company_name = match.group("company_name")
                if company_name not in self.unique_companies:
                    company_location = match.group("company_region")
                    company_uri = match.group("company_uri")
                    json_url = self.platform_config['url_format'].format(
                        company_name=company_name,
                        company_region=company_location,
                        company_uri=company_uri
                    )
                    self.companies.append(
                        {'name': company_name, 'url': json_url, 'platform': self.platform})
                    self.unique_companies.add(company_name)
        except (AttributeError, IndexError, re.error) as err:
            print(f"Error processing MyWorkDayJobs link: {err}")
