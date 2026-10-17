import uuid
from typing import AsyncGenerator, Callable, List, Optional
from fastapi import Depends, Query, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding an async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

def get_request_id(request: Request) -> str:
    """Extracts the active correlation ID from the request state."""
    return getattr(request.state, "request_id", "unknown")

class PaginationParams:
    """Standardized pagination and sorting query parameters."""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number starting at 1"),
        limit: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
        sort: Optional[str] = Query(None, description="Field name to sort by"),
        order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction: asc or desc")
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit
        self.sort = sort
        self.order = order.lower()

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validates the Bearer access token and returns the current user."""
    if not token:
        raise UnauthorizedException(
            message="Authentication credentials were not provided",
            code="NOT_AUTHENTICATED"
        )

    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(
            message="Invalid token claims",
            code="INVALID_TOKEN_CLAIMS"
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException(
            message="Malformed user identifier in token",
            code="MALFORMED_TOKEN"
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException(
            message="User account no longer exists",
            code="USER_NOT_FOUND"
        )

    if not user.is_active:
        raise UnauthorizedException(
            message="Account has been deactivated",
            code="ACCOUNT_DEACTIVATED"
        )

    return user

async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Extracts the user if a valid token is provided, otherwise returns None (for anonymous endpoints)."""
    if not token:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except UnauthorizedException:
        return None

def require_role(*roles: UserRole) -> Callable[[User], User]:
    """Dependency factory ensuring the current user possesses one of the required roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role
        if user_role not in roles:
            required_names = [r.value for r in roles]
            raise ForbiddenException(
                message=f"Insufficient permissions. Action requires one of: {required_names}",
                code="FORBIDDEN_ROLE"
            )
        return current_user

    return role_checker

# Predefined role dependencies
require_admin = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
require_super_admin = require_role(UserRole.SUPER_ADMIN)
