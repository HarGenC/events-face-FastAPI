import asyncio
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from loguru import logger

from app.api.endpoints import router
from app.core import handlers
from app.workers.sync_worker import sync_worker

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger.remove()
logger.add(sys.stderr, colorize=True, format="{time:HH:mm:ss} | {level} | {message}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")
    task = asyncio.create_task(sync_worker())

    yield

    logger.info("Stopping lifespan")

    task.cancel()


app = FastAPI(title="events-face", lifespan=lifespan)

app.add_exception_handler(RequestValidationError, handlers.validation_exception_handler)
app.add_exception_handler(HTTPException, handlers.http_exception_handler)
app.add_exception_handler(Exception, handlers.global_exception_handler)

app.include_router(router)
