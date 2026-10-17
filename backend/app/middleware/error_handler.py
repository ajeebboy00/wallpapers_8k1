from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException
from app.core.logging import logger

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catches any unhandled exceptions during request dispatch and formats a consistent 500 response."""
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except AppException as exc:
            logger.warning(
                f"Application error [{exc.code}] on {request.method} {request.url.path}: {exc.message}"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                        "details": exc.details
                    }
                }
            )
        except Exception as exc:
            logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected internal server error occurred."
                    }
                }
            )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for all domain and application exceptions."""
    logger.warning(f"AppException [{exc.code}] on {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Standardizes Starlette HTTP exceptions (404, 405, etc.) into the API error format."""
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT",
        413: "PAYLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE"
    }
    code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    message = str(exc.detail) if exc.detail else "An HTTP error occurred"
    
    logger.info(f"HTTPException [{code}] on {request.method} {request.url.path}: {message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": None
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats Pydantic validation errors into clean field-level error details."""
    details = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
        details.append({
            "field": field_path,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error")
        })

    logger.warning(f"Validation failure on {request.method} {request.url.path}: {len(details)} errors")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request parameters or payload failed validation.",
                "details": details
            }
        }
    )
