import logging
import os

from celery import Celery

logger = logging.getLogger("celery")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.info(f"Celery debug task called. Request id: {self.request.id}")
