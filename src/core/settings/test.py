from .base import *  # noqa

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True  # чтобы исключения падали в тестах

LOG_LEVEL = "DEBUG"
