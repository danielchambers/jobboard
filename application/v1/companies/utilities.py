from typing import Dict
from application.models.jobs import Company


def company_to_dict(company: Company) -> Dict[str, str]:
    """
    Convert a Company instance to a dictionary.

    Args:
        company (Company): The Company instance to convert.

    Returns:
        Dict[str, str]: A dictionary containing the Company's attributes.
            The keys are attribute names, and the values are their corresponding values
            converted to strings.

    """
    return {
        "id": company.id,
        "company": company.company,
        "url": company.url,
        "platform": company.platform,
        "total_jobs": company.total_jobs,
        "found_date": company.found_date,
        "is_active": company.is_active,
    }
