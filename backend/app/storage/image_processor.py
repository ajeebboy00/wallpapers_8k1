import io
import os
from dataclasses import dataclass
from typing import Optional, Tuple
from PIL import Image

from app.core.constants import MAX_IMAGE_UPLOAD_BYTES
from app.core.exceptions import BadRequestException
from app.core.logging import logger

# Prevent decompression bomb attacks while accommodating 8K+ imagery (up to 100 megapixels)
Image.MAX_IMAGE_PIXELS = 100_000_000

@dataclass
class ProcessedImageResult:
    original_bytes: bytes
    original_extension: str
    optimized_bytes: bytes
    preview_bytes: bytes
    thumbnail_bytes: bytes
    width: int
    height: int
    aspect_ratio: float
    file_size: int
    file_format: str
    resolution: str

class ImageProcessor:
    """Production image processing pipeline generating multi-variant WebP assets with Pillow."""

    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

    @classmethod
    def classify_resolution(cls, width: int, height: int) -> str:
        """Classifies image resolution based on dimensions and total pixel count."""
        max_dim = max(width, height)
        pixels = width * height

        if max_dim >= 7680 or pixels >= 30_000_000:
            return "8K"
        elif max_dim >= 3840 or pixels >= 8_000_000:
            return "4K"
        elif max_dim >= 2560 or pixels >= 3_600_000:
            return "2K"
        elif max_dim >= 1920 or pixels >= 2_000_000:
            return "FHD"
        elif max_dim >= 1280:
            return "HD"
        return "SD"

    @classmethod
    def _resize_proportional(cls, img: Image.Image, max_dimension: int) -> Image.Image:
        """Resizes image proportionally using Lanczos resampling if dimensions exceed max_dimension."""
        w, h = img.size
        if max(w, h) <= max_dimension:
            return img.copy()

        if w >= h:
            new_w = max_dimension
            new_h = max(1, int(h * (max_dimension / w)))
        else:
            new_h = max_dimension
            new_w = max(1, int(w * (max_dimension / h)))

        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    @classmethod
    def _encode_webp(cls, img: Image.Image, quality: int = 85) -> bytes:
        """Encodes PIL Image to WebP binary bytes buffer."""
        # Convert CMYK or Palette images to RGB/RGBA for clean WebP compatibility
        if img.mode in ("CMYK", "P"):
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=quality, method=4)
        return buffer.getvalue()

    @classmethod
    def process_image(cls, file_bytes: bytes, filename: str = "upload.jpg") -> ProcessedImageResult:
        """Validates uploaded image and generates original, optimized, preview, and thumbnail variants."""
        # 1. Enforce file size limit
        file_size = len(file_bytes)
        if file_size > MAX_IMAGE_UPLOAD_BYTES:
            max_mb = MAX_IMAGE_UPLOAD_BYTES // (1024 * 1024)
            raise BadRequestException(
                f"File size exceeds maximum permitted limit of {max_mb} MB",
                code="FILE_TOO_LARGE"
            )

        if file_size == 0:
            raise BadRequestException("Uploaded file is empty", code="EMPTY_FILE")

        # 2. Validate image structure & header magic bytes via Pillow
        try:
            test_img = Image.open(io.BytesIO(file_bytes))
            detected_format = test_img.format
            test_img.verify()
        except Exception as exc:
            logger.warning(f"Corrupted or invalid image upload rejected: {exc}")
            raise BadRequestException(
                "Uploaded file is corrupted or not a valid image",
                code="INVALID_IMAGE_FILE"
            )

        if not detected_format or detected_format.upper() not in cls.ALLOWED_FORMATS:
            raise BadRequestException(
                f"Unsupported image format '{detected_format}'. Supported formats: JPEG, PNG, WEBP",
                code="UNSUPPORTED_FORMAT"
            )

        # 3. Re-open image for processing after verification
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size
        aspect_ratio = round(width / height, 4) if height > 0 else 1.0
        resolution = cls.classify_resolution(width, height)
        file_format = detected_format.lower()

        # Determine original file extension
        ext = os.path.splitext(filename)[1].lower()
        if not ext or ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = f".{file_format}"
            if ext == ".jpeg":
                ext = ".jpg"

        # 4. Generate multi-variant tiers
        # Variant A: Optimized (Max dimension 3840px, Quality 90)
        img_optimized = cls._resize_proportional(img, max_dimension=3840)
        optimized_bytes = cls._encode_webp(img_optimized, quality=90)

        # Variant B: Preview (Max dimension 1920px, Quality 85)
        img_preview = cls._resize_proportional(img, max_dimension=1920)
        preview_bytes = cls._encode_webp(img_preview, quality=85)

        # Variant C: Thumbnail (Max dimension 600px, Quality 80)
        img_thumb = cls._resize_proportional(img, max_dimension=600)
        thumbnail_bytes = cls._encode_webp(img_thumb, quality=80)

        logger.info(
            f"Processed image: {width}x{height} ({resolution}) [{file_format}] -> "
            f"Original: {file_size}B, Optimized: {len(optimized_bytes)}B, "
            f"Preview: {len(preview_bytes)}B, Thumb: {len(thumbnail_bytes)}B"
        )

        return ProcessedImageResult(
            original_bytes=file_bytes,
            original_extension=ext,
            optimized_bytes=optimized_bytes,
            preview_bytes=preview_bytes,
            thumbnail_bytes=thumbnail_bytes,
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            file_size=file_size,
            file_format=file_format,
            resolution=resolution
        )
