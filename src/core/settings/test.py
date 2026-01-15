from .base import *  # noqa
from .base import DATABASES, os

DATABASES["default"]["NAME"] = os.environ.get("POSTGRES_DB_TEST")

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True  # чтобы исключения падали в тестах

LOG_LEVEL = "DEBUG"
