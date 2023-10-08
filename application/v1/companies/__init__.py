from sqlalchemy import func, or_
from fastapi import APIRouter, Query, HTTPException
from application.database import database_context
from application.models.jobs import Company
from application.v1.companies.utilities import company_to_dict

companies_router = APIRouter(
    prefix="/v1/companies"
)


@companies_router.get('/')
def return_all_company_names(
    q: str | None = None,
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit")
):
    with database_context() as db:
        query_base = db.query(Company)

        if q:
            filtered_query = query_base.filter(
                or_(Company.name == q, Company.name.ilike(f"%{q}%")))
        else:
            filtered_query = query_base
        offset = (page - 1) * limit if page > 0 else 0
        records = filtered_query.offset(offset).limit(limit).all()
        total_records = filtered_query.count()
        return_data = {
            'total': total_records,
            'results': [company_to_dict(record) for record in records]
        }

        return return_data


@companies_router.get('/{company}')
def return_one_company_name(company):
    with database_context() as db:
        records = db.query(Company).filter_by(name=company).all()

        if not records:
            raise HTTPException(status_code=404, detail="Company not found")

        return_data = {
            'total': len(records),
            'results': [company_to_dict(record) for record in records]
        }

        return return_data
