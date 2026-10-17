from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse

class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    exp: int
    token_type: str = "access"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20, description="Opaque refresh token string")
