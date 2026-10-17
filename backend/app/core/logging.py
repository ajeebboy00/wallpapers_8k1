import contextvars
import logging
import re
import sys
from typing import Optional
from app.core.config import settings

# Context variable to hold the active request correlation ID
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id_ctx", default=None)

SENSITIVE_PATTERNS = [
    (re.compile(r'(password|passwd|pwd|secret|token|api_key|authorization)["\']?\s*[:=]\s*["\']?([^"\'\s&]+)', re.IGNORECASE), r'\1=***REDACTED***'),
    (re.compile(r'postgresql\+[^:]+://[^:]+:([^@]+)@', re.IGNORECASE), r'postgresql+***:***@'),
    (re.compile(r'Bearer\s+([A-Za-z0-9\-_\.]+)', re.IGNORECASE), r'Bearer ***REDACTED***'),
]

class SensitiveDataFilter(logging.Filter):
    """Redacts sensitive credentials, authorization tokens, and secrets from logs."""
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern, replacement in SENSITIVE_PATTERNS:
                msg = pattern.sub(replacement, msg)
            record.msg = msg
        return True

class RequestIdFilter(logging.Filter):
    """Injects current request_id into log records."""
    def filter(self, record: logging.LogRecord) -> bool:
        req_id = request_id_ctx.get()
        record.request_id = f"[{req_id}]" if req_id else "[-]"
        return True

def setup_logging():
    log_level = logging.DEBUG if settings.APP_DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(request_id)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Silence overly noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)

logger = logging.getLogger("w8k1")
