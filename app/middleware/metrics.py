import time

from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.metrics import http_request_duration_seconds, http_requests_total


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.monotonic()

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception:
            status_code = 500
            raise

        finally:
            duration = time.monotonic() - start_time

            route = request.scope.get("route")
            endpoint = route.path if route else "unknown"

            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=status_code,
            ).inc()

            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint,
            ).observe(duration)
