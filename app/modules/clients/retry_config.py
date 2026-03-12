import http
from typing import Set


class RetryConfig:
    def __init__(
        self,
        retryable_statuses: Set[http.HTTPStatus] = None,
        base_delay: float = 1.0,
        max_retries: int = 3,
        backoff: float = 2.0,
    ):
        if retryable_statuses is None:
            self.retryable_statuses = {
                http.HTTPStatus.REQUEST_TIMEOUT,  # 408
                http.HTTPStatus.TOO_MANY_REQUESTS,  # 429
                http.HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
                http.HTTPStatus.BAD_GATEWAY,  # 502
                http.HTTPStatus.SERVICE_UNAVAILABLE,  # 503
                http.HTTPStatus.GATEWAY_TIMEOUT,  # 504
            }
        else:
            self.retryable_statuses = retryable_statuses
        self.base_delay = base_delay
        self.max_retries = max_retries
        self.backoff = backoff
