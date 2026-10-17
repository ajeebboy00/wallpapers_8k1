from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.token import RefreshTokenRequest, TokenResponse
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=StandardResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
async def register(
    payload: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    device_info = request.headers.get("User-Agent")
    service = AuthService(db)
    token_response = await service.register(payload, device_info=device_info)
    return StandardResponse(
        success=True,
        data=token_response,
        message="Account registered successfully"
    )

@router.post(
    "/login",
    response_model=StandardResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT and refresh token"
)
async def login(
    payload: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    device_info = request.headers.get("User-Agent")
    service = AuthService(db)
    token_response = await service.login(payload, device_info=device_info)
    return StandardResponse(
        success=True,
        data=token_response,
        message="Login successful"
    )

@router.post(
    "/refresh",
    response_model=StandardResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and retrieve new access token"
)
async def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    device_info = request.headers.get("User-Agent")
    service = AuthService(db)
    token_response = await service.refresh_tokens(payload.refresh_token, device_info=device_info)
    return StandardResponse(
        success=True,
        data=token_response,
        message="Tokens refreshed successfully"
    )

@router.post(
    "/logout",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Revoke refresh token and invalidate session"
)
async def logout(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    revoked = await service.logout(payload.refresh_token)
    return StandardResponse(
        success=True,
        data={"revoked": revoked},
        message="Successfully logged out"
    )

@router.post(
    "/forgot-password",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Request a password reset link/token"
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    token = await service.forgot_password(payload.email)
    return StandardResponse(
        success=True,
        data={"message": "Password reset instructions processed", "reset_token": token},
        message="Password reset initiated"
    )

@router.post(
    "/reset-password",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Reset password using a valid reset token"
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    success = await service.reset_password(payload.token, payload.new_password)
    return StandardResponse(
        success=success,
        data={"updated": success},
        message="Password reset successfully"
    )

@router.get(
    "/me",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve authenticated user profile"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return StandardResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        message="Current user retrieved"
    )
