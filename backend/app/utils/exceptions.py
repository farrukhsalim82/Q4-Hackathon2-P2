"""
[Task]: T-B010
[From]: speckit.plan §3.2
[Purpose]: Global exception handlers — consistent JSON error responses, no stack trace leaks
"""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _status_to_code(status: int) -> str:
    """Map HTTP status code to application error code."""
    codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
        503: "DB_ERROR",
    }
    return codes.get(status, "UNKNOWN_ERROR")


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
                "code": _status_to_code(exc.status_code),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "code": "INTERNAL_ERROR",
            },
        )
