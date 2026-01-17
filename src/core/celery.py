import logging
import os

from celery import Celery, signals

from core.tracing import ensure_trace_id, set_trace_id

logger = logging.getLogger("celery")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


def _extract_trace_id(task):
    request = getattr(task, "request", None)
    if not request:
        return None

    headers = getattr(request, "headers", None) or {}
    return headers.get("trace_id") or headers.get("X-Request-ID")


@signals.task_prerun.connect
def set_trace_id_from_headers(task=None, **kwargs):
    trace_id = _extract_trace_id(task)
    if trace_id:
        set_trace_id(trace_id)
    else:
        ensure_trace_id()


@signals.task_postrun.connect
def clear_trace_id(**kwargs):
    set_trace_id(None)


@app.task(bind=True)
def debug_task(self):
    logger.info(f"Celery debug task called. Request id: {self.request.id}")
