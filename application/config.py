import os
from functools import lru_cache
from celery.schedules import crontab


class BaseConfig:
    CELERY_broker_url: str = os.getenv("CELERY_BROKER_URL")
    result_backend: str = os.getenv("CELERY_RESULT_BACKEND")
    CELERY_TIMEZONE = 'America/Los_Angeles'
    CELERY_BEAT_SCHEDULE: dict = {
        "task-find-greenhouse-company-names": {
            "task": "application.periodic_tasks.main.collect_companies",
            "schedule": 40000.0,  # 60 minutes
            'args': ['greenhouse', 'Los Angeles python', 'm1'],
        },
        "task-find-lever-company-names": {
            "task": "application.periodic_tasks.main.collect_companies",
            "schedule": 42000.0,  # 70 minutes
            'args': ['lever', 'Los Angeles python', 'm1'],
        },
        "task-find-careerpuck-company-names": {
            "task": "application.periodic_tasks.main.collect_companies",
            "schedule": 48000.0,  # 80 minutes
            'args': ['careerpuck', 'Los Angeles python', 'm1'],
        },
        "task-find-ashbyhq-company-names": {
            "task": "application.periodic_tasks.main.collect_companies",
            "schedule": 54000.0,  # 90 minutes
            'args': ['ashbyhq', 'Los Angeles python', 'm1'],
        },
        "task-find-myworkdayjobs-company-names": {
            "task": "application.periodic_tasks.main.collect_companies",
            "schedule": 60000.0,  # 100 minutes
            'args': ['myworkdayjobs', 'Los Angeles python', 'm1'],
        },
        "task-get-company-jobs": {
            "task": "application.periodic_tasks.main.collect_jobs",
            "schedule": crontab(hour=16, minute=46),
            # "schedule": 60.0,
            "args": ["lever"]
        }
    }


class DevelopmentConfig(BaseConfig):
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DATABASE: str = os.getenv('POSTGRES_DATABASE')
    DATABASE_CONNECT_DICT: dict = {"check_same_thread": False}
    DATABASE_URL: str = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/{os.getenv('POSTGRES_DATABASE')}"


class ProductionConfig(BaseConfig):
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DATABASE: str = os.getenv('POSTGRES_DATABASE')
    DATABASE_CONNECT_DICT: dict = {"check_same_thread": False}


class TestingConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_CONNECT_DICT: dict = {"check_same_thread": False}


@lru_cache()
def get_settings():
    config_class = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.getenv("FASTAPI_CONFIG", 'development')
    configuration = config_class[config_name]
    return configuration()


settings = get_settings()
