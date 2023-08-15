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
        "task-schedule-work": {
            "task": "application.periodic_tasks.main.test",
            "schedule": 5.0,
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
