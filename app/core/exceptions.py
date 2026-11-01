"""
Standardized application exceptions and FastAPI exception handlers.
Ensures uniform error JSON contract:
{ "error": { "code": "...", "message": "...", "request_id": "..." } }
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import uuid


class AppBaseException(Exception):
    """Base exception for ResearchLens AI application."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class DocumentValidationError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message=message, code="DOCUMENT_VALIDATION_ERROR", status_code=400)


class DocumentNotFoundError(AppBaseException):
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document '{document_id}' was not found.",
            code="DOCUMENT_NOT_FOUND",
            status_code=404
        )


class LLMExecutionError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message=message, code="LLM_EXECUTION_ERROR", status_code=502)


class InsufficientEvidenceError(AppBaseException):
    def __init__(self, message: str = "Insufficient evidence to answer this question."):
        super().__init__(message=message, code="INSUFFICIENT_EVIDENCE", status_code=422)


def get_request_id(request: Request) -> str:
    """Retrieve or generate correlation request ID."""
    return getattr(request.state, "request_id", uuid.uuid4().hex[:8])


async def app_exception_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = get_request_id(request)
    code = "HTTP_ERROR"
    if exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 400:
        code = "BAD_REQUEST"
    elif exc.status_code == 422:
        code = "UNPROCESSABLE_ENTITY"
    elif exc.status_code >= 500:
        code = "SERVER_ERROR"

    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc) or "An unexpected server error occurred.",
                "request_id": request_id
            }
        }
    )

