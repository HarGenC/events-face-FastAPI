from fastapi import FastAPI

from app.middleware.metrics import MetricsMiddleware
from app.observability.endpoints import router as metrics_router


def setup_observability(app: FastAPI):
    app.add_middleware(MetricsMiddleware)
    app.include_router(metrics_router)
