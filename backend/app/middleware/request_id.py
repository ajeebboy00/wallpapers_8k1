import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_ctx

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assigns or propagates an X-Request-ID header to every request/response and logs context."""
    async def dispatch(self, request: Request, call_next) -> Response:
        incoming_id = request.headers.get("X-Request-ID")
        request_id = incoming_id if incoming_id else uuid.uuid4().hex

        # Set context variable for structured logging
        token = request_id_ctx.set(request_id)
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)
