"""Error management: classify errors, record them, build reports."""
import requests

class ScraperError(Exception): pass
class ValidationError(ScraperError): pass
class PermissionDenied(ScraperError): pass

RETRYABLE_STATUS = {429, 500, 502, 503, 504}

def is_retryable(exc: Exception) -> bool:
    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return exc.response.status_code in RETRYABLE_STATUS
    return False

class ErrorTracker:
    def __init__(self, logger):
        self.logger, self.errors = logger, []

    def record(self, context: str, exc: Exception):
        self.errors.append({"context": context, "type": type(exc).__name__, "message": str(exc)})
        self.logger.error("%s: %s", context, exc)
