import contextvars

_trace_id_var = contextvars.ContextVar("trace_id", default=None)


def get_trace_id() -> str:
    trace_id = _trace_id_var.get()
    return trace_id


def set_trace_id(trace_id: str):
    _trace_id_var.set(trace_id)
