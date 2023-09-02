from application.models.jobs import Company
from application.v1.companies.utilities import company_to_dict


def test_company_to_dict():
    mock_company = Company(
        id=1,
        company="netflix",
        url="http://netflix.com",
        platform="greenhouse",
        total_jobs=100,
        found_date="2023-08-30",
        is_active=True,
    )
    expected_results = {
        "id": 1,
        "company": "netflix",
        "url": "http://netflix.com",
        "platform": "greenhouse",
        "total_jobs": 100,
        "found_date": "2023-08-30",
        "is_active": True,
    }
    result = company_to_dict(mock_company)

    assert result == expected_results
