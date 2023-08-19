
from fastapi import APIRouter

companies_router = APIRouter(
    prefix="/v1/companies"
)


@companies_router.get('/{company}')
def company_job_listing(company):
    return {"jobs": [{'a': 'a'}], 'total': 1, 'company': company}
