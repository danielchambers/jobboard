from fastapi import APIRouter, Query
from sqlalchemy.sql import func, text
from sqlalchemy.orm import Query as SQLAlchemyQuery
from application.database import database_context
from application.models.jobs import Company

companies_router = APIRouter(
    prefix="/v1/companies"
)


@companies_router.get('/')
def return_all_company_names(
    q: str | None = None,
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit")
):
    if q:
        return {'endpoint': f'/q={q}&page={page}&limit={limit}'}
    else:
        return {'endpoint': '/'}


@companies_router.get('/{company_name}')
def return_one_company_name(company_name):
    with database_context() as db:
        return {'endpoint': f'{company_name}'}


# @companies_router.get('/')
# def return_search_company_names(
#     q: str | None = None,
#     page: int = Query(1, alias="page"),
#     limit: int = Query(10, alias="limit")
# ):
#     print(page, limit)
#     return {'endpoint': f'/q={q}'}
    # with database_context() as db:
    #     endpoint_results = {'q': q}
    #     if q:
    #         query: SQLAlchemyQuery = db.query(GreenhouseJob).filter(
    #             func.to_tsvector('english', GreenhouseJob.title).op(
    #                 '@@')(f"'{q}'")
    #         )
    #     else:
    #         query: SQLAlchemyQuery = db.query(GreenhouseJob)

    #     total_results = query.count()
    #     results = query.offset((page - 1) * limit).limit(limit).all()
    #     jobs = [{'title': result.title, 'location': result.location}
    #             for result in results]
    #     endpoint_results.update({'jobs': jobs, 'total': total_results})
    # return endpoint_results
