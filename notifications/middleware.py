import logging
import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class Middleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Pre execution response code
        start = time.perf_counter()

        response = self.get_response(request)
        # Post execution response code

        elapsed_time = (time.perf_counter() - start) * 1000
        logger.info(
            f"[{request.method}] '{request.path}', "
            f"Status: {response.status_code}, Elapsed: {elapsed_time}"
        )

        return response
