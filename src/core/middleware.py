from django.utils.deprecation import MiddlewareMixin

from core.tracing import ensure_trace_id, get_trace_id


class TraceIdMiddleware(MiddlewareMixin):
    def process_request(self, request):
        trace_id = ensure_trace_id(request.headers.get("X-Request-ID"))
        request.META["HTTP_X_REQUEST_ID"] = trace_id

    def process_response(self, request, response):
        trace_id = get_trace_id()
        response["X-Request-ID"] = trace_id
        return response
