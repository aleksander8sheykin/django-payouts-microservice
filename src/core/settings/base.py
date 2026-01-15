import os
from pathlib import Path

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ALLOWED_HOSTS = ["*"]

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ["DJANGO_DEBUG"] == "True"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "payouts",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "core.middleware.TraceIdMiddleware",
]

ROOT_URLCONF = "core.urls"

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]
CELERY_RESULT_BACKEND = os.environ["CELERY_RESULT_BACKEND"]
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = os.environ["CELERY_TASK_TIME_LIMIT"]
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_BEAT_SCHEDULE = {
    "reconcile-payouts": {
        "task": "payouts.tasks.reconcile_processing_payouts",
        "schedule": crontab(minute="*/5"),
    }
}

LOG_LEVEL = os.environ["LOG_LEVEL"].upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "trace_id": {
            "()": "core.logging_filters.TraceIdFilter",
        },
    },
    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] [{trace_id}] [{name}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": "ext://sys.stdout",
            "filters": ["trace_id"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "celery": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
        "propagate": True,
        "filters": ["trace_id"],
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
