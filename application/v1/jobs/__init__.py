from sqlalchemy import func
from fastapi import APIRouter, Query
from application.database import database_context
from application.models.jobs import Job, Company

jobs_router = APIRouter(prefix='/v1/jobs')


@jobs_router.get('/')
def get_job(
    q: str | None = None,
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit")
):
    with database_context() as db:
        if q:
            # Split the query into separate terms
            search_terms = q.split()

            # Check if there's more than one term to perform an exact phrase search
            if len(search_terms) > 1:
                # Construct the tsquery for an exact phrase search
                search_query = f"'{' & '.join(search_terms)}'"
            else:
                # Construct the tsquery for individual terms
                search_query = f"'{' | '.join(search_terms)}'"

            # Perform the full-text search using the constructed tsquery
            search_vector = func.to_tsquery('english', search_query)

            offset = (page - 1) * limit if page > 0 else 0

            # Join the Company table and select the name attribute
            query = db.query(Job, Company.name).join(Company).filter(
                Job.title_vector.op('@@')(search_vector)
            ).offset(offset).limit(limit)

            # Execute the query and retrieve the results
            records = query.all()

            total_records = db.query(func.count(Job.id)).filter(
                Job.title_vector.op('@@')(search_vector)).scalar()

        else:
            # Handle the case when no search query is provided
            records = []
            total_records = 0

        return_data = {
            'total': total_records,
            'results': [{'title': record[0].title, 'company': record[1]} for record in records]
        }
        return return_data
