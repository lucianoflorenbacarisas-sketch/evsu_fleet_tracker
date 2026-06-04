import logging


class ExceptionLoggingMiddleware:
    """Log unhandled exceptions with traceback for easier debugging."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.request')

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            self.logger.exception('Unhandled exception during request: %s %s', request.method, request.path)
            raise
