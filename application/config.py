import os
from functools import lru_cache


class BaseConfig:
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DATABASE: str = os.getenv('POSTGRES_DATABASE')
    DATABASE_CONNECT_DICT: dict = {
        "check_same_thread": False
    }

    CELERY_broker_url: str = os.getenv("CELERY_BROKER_URL")
    result_backend: str = os.getenv("CELERY_RESULT_BACKEND")
    CELERY_BEAT_SCHEDULE: dict = {
        "task-find-greenhouse-company-names": {
            "task": "application.periodic_tasks.main.company_names",
            "schedule": 3600.0,
            'args': ('greenhouse', 'CA', 'fullstack developer'),
        },
        "task-find-lever-company-names": {
            "task": "application.periodic_tasks.main.company_names",
            "schedule": 3900.0,
            'args': ('lever', 'CA', 'fullstack developer'),
        },
        "task-download-greenhouse-company-jobs": {
            "task": "application.periodic_tasks.main.greenhouse_jobs",
            "schedule": 1800.0
        }
    }


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_class = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.getenv("FASTAPI_CONFIG")
    configuration = config_class[config_name]
    return configuration()


settings = get_settings()
