import os
import sys
from contextlib import asynccontextmanager

import sentry_sdk
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from loguru import logger
from prometheus_client import REGISTRY, generate_latest
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.api.endpoints import router
from app.core import handlers
from app.core.config import settings
from app.middleware.metrics import MetricsMiddleware
from app.workers.outbox_worker import outbox_worker
from app.workers.sync_worker import sync_worker

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger.remove()
logger.add(sys.stderr, colorize=True, format="{time:HH:mm:ss} | {level} | {message}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        sync_worker,
        trigger=CronTrigger(hour=6, minute=0),
        id="sync_worker_job",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        outbox_worker,
        trigger=CronTrigger(second="*/30"),
        id="outbox_worker_job",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()

    yield

    logger.info("Stopping lifespan")

    scheduler.shutdown()


app = FastAPI(title="events-face", lifespan=lifespan)
sentry_sdk.init(dsn=settings.SENTRY_DSN)
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(MetricsMiddleware)

app.add_exception_handler(RequestValidationError, handlers.validation_exception_handler)
app.add_exception_handler(HTTPException, handlers.http_exception_handler)
app.add_exception_handler(Exception, handlers.global_exception_handler)


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain",
    )


app.include_router(router)
