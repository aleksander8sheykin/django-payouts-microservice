import contextvars
import re
import secrets

TRACE_ID_BYTES = 16
TRACE_ID_DEFAULT = "-"
TRACE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,63}$")

_trace_id_var = contextvars.ContextVar("trace_id", default=None)


def normalize_trace_id(trace_id: str | None) -> str | None:
    if not trace_id:
        return None

    normalized = trace_id.strip()
    if not normalized:
        return None

    if not TRACE_ID_PATTERN.match(normalized):
        return None

    return normalized.lower()


def generate_trace_id() -> str:
    return secrets.token_hex(TRACE_ID_BYTES)


def ensure_trace_id(incoming: str | None = None) -> str:
    trace_id = normalize_trace_id(incoming)
    if not trace_id:
        trace_id = generate_trace_id()
    _trace_id_var.set(trace_id)
    return trace_id


def get_trace_id() -> str:
    trace_id = _trace_id_var.get()
    return trace_id or TRACE_ID_DEFAULT


def set_trace_id(trace_id: str | None):
    if trace_id is None:
        _trace_id_var.set(None)
        return

    normalized = normalize_trace_id(trace_id)
    _trace_id_var.set(normalized or generate_trace_id())
