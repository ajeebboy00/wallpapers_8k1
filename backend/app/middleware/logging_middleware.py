import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming HTTP requests, duration in milliseconds, and status codes."""
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # Process the request
        response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"

        # Log request completion with timing
        log_level = logger.info if response.status_code < 400 else (logger.warning if response.status_code < 500 else logger.error)
        log_level(
            f"{method} {path} HTTP/{request.scope.get('http_version', '1.1')} "
            f"-> {response.status_code} [{process_time_ms:.2f}ms] (Client: {client_host})"
        )

        return response
