from typing import Any, Optional
from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "BAD_REQUEST",
        message: str = "An error occurred",
        details: Optional[Any] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details

class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request", code: str = "BAD_REQUEST", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, code=code, message=message, details=details)

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, code=code, message=message)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Invalid or expired authentication credentials", code: str = "UNAUTHORIZED"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, code=code, message=message)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Insufficient permissions to perform this action", code: str = "FORBIDDEN"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, code=code, message=message)

class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict", code: str = "CONFLICT"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, code=code, message=message)

class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, code="VALIDATION_ERROR", message=message, details=details)

class RateLimitException(AppException):
    def __init__(self, message: str = "Too many requests. Please slow down and try again later.", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, code="RATE_LIMIT_EXCEEDED", message=message, details=details)

class InternalServerException(AppException):
    def __init__(self, message: str = "An unexpected internal server error occurred.", code: str = "INTERNAL_SERVER_ERROR"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, code=code, message=message)
