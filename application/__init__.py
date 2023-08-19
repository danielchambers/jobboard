from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    from application.celery import create_celery
    app.celery_app = create_celery()

    from application.periodic_tasks import main

    from application.v1.companies import companies_router
    app.include_router(companies_router)

    @app.get("/")
    async def root():
        return {"message": "Hello World!"}

    return app
