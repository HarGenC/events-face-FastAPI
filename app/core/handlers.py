import traceback
from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger


async def global_exception_handler(request: Request, exc: Exception):
    short_tb = "".join(traceback.format_exception_only(type(exc), exc))

    logger.bind(path=request.url.path, method=request.method).error(
        "Unhandled error {}", short_tb
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # собираем ошибки Pydantic в читаемом виде
    errors = exc.errors()

    logger.bind(path=request.url.path, method=request.method, errors=errors).warning(
        "Request validation failed"
    )

    return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": errors})


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.bind(
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail,
    ).info("HTTPException raised")

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
