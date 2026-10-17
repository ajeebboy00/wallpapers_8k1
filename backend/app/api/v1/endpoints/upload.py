from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.upload import ImageUploadResponse
from app.services.upload_service import UploadService

router = APIRouter(prefix="/storage", tags=["Storage"])

@router.post(
    "/upload",
    response_model=StandardResponse[ImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload image asset and generate multi-tier variants (Admin only)"
)
async def upload_image(
    file: UploadFile = File(..., description="Raw image file (JPEG, PNG, WEBP)"),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Processes uploaded image into Original, Optimized (4K), Preview (FHD), and Thumbnail (600px) WebP assets."""
    file_bytes = await file.read()
    service = UploadService(db)
    response_data, _ = await service.process_and_store_image(
        file_bytes=file_bytes,
        filename=file.filename or "wallpaper.jpg"
    )

    return StandardResponse(
        success=True,
        data=response_data,
        message="Image processed and stored successfully in all 4 resolution variants"
    )
