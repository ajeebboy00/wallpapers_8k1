import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import UserRole
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    generate_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
    verify_password_reset_token,
)
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenResponse
from app.schemas.user import UserLoginRequest, UserRegisterRequest, UserResponse

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = TokenRepository(session)

    async def _issue_token_pair(self, user: User, device_info: Optional[str] = None) -> TokenResponse:
        """Helper to create a JWT access token and a persisted refresh token."""
        # 1. Access Token
        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # 2. Opaque Refresh Token + SHA-256 Hash
        raw_refresh_token, token_hash = generate_refresh_token()
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await self.token_repo.create_token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=refresh_expires_at,
            device_info=device_info
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )

    async def register(self, data: UserRegisterRequest, device_info: Optional[str] = None) -> TokenResponse:
        """Registers a new user account, validating uniqueness and issuing token pair."""
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictException(
                message=f"An account with email '{data.email}' already exists.",
                code="EMAIL_ALREADY_EXISTS"
            )

        hashed_password = get_password_hash(data.password)
        user = await self.user_repo.create_user(
            name=data.name,
            email=data.email,
            password_hash=hashed_password,
            role=UserRole.USER,
            is_active=True,
            email_verified=False
        )

        logger.info(f"Registered new user account: {user.email} [{user.id}]")
        return await self._issue_token_pair(user, device_info)

    async def login(self, data: UserLoginRequest, device_info: Optional[str] = None) -> TokenResponse:
        """Authenticates user via email and password, returning tokens on success."""
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            raise UnauthorizedException(
                message="Invalid email or password",
                code="INVALID_CREDENTIALS"
            )

        if not verify_password(data.password, user.password_hash):
            raise UnauthorizedException(
                message="Invalid email or password",
                code="INVALID_CREDENTIALS"
            )

        if not user.is_active:
            raise UnauthorizedException(
                message="Account has been deactivated. Please contact support.",
                code="ACCOUNT_DEACTIVATED"
            )

        await self.user_repo.update_last_login(user.id)
        logger.info(f"User authenticated: {user.email} [{user.id}]")
        return await self._issue_token_pair(user, device_info)

    async def refresh_tokens(self, refresh_token_str: str, device_info: Optional[str] = None) -> TokenResponse:
        """Rotates a refresh token and generates a new access token pair."""
        token_hash = hash_token(refresh_token_str)
        token_record = await self.token_repo.get_valid_token(token_hash)

        if not token_record:
            raise UnauthorizedException(
                message="Invalid, expired, or revoked refresh token",
                code="INVALID_REFRESH_TOKEN"
            )

        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException(
                message="Account is inactive or does not exist",
                code="USER_INACTIVE"
            )

        # Token Rotation: Revoke old refresh token before issuing a new one
        await self.token_repo.revoke_token(token_hash)

        # Issue new token pair
        return await self._issue_token_pair(user, device_info)

    async def logout(self, refresh_token_str: str) -> bool:
        """Revokes the refresh token upon logout."""
        token_hash = hash_token(refresh_token_str)
        return await self.token_repo.revoke_token(token_hash)

    async def forgot_password(self, email: str) -> str:
        """Generates a password reset token (architecture ready for mail delivery)."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Avoid user enumeration: log warning but return uniform response
            logger.info(f"Password reset requested for non-existent email: {email}")
            return "If an account exists with this email, instructions have been sent."

        reset_token = create_password_reset_token(user.email)
        logger.info(f"Generated password reset token for: {user.email}")
        return reset_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Validates password reset token, updates password, and revokes all active sessions."""
        email = verify_password_reset_token(token)
        if not email:
            raise BadRequestException(
                message="Password reset token is invalid or has expired",
                code="INVALID_RESET_TOKEN"
            )

        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundException("User not found", code="USER_NOT_FOUND")

        user.password_hash = get_password_hash(new_password)
        await self.session.flush()

        # Invalidate all active sessions for security
        await self.token_repo.revoke_all_user_tokens(user.id)
        logger.info(f"Password successfully reset for: {user.email}")
        return True
