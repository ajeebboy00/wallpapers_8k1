import io
import os
import uuid
import pytest
from httpx import AsyncClient
from fastapi import status
from PIL import Image

from app.core.exceptions import BadRequestException
from app.models.category import Category
from app.storage.image_processor import ImageProcessor
from app.storage.local import LocalStorageProvider

def make_synthetic_image(width: int, height: int, format: str = "JPEG", color: tuple = (25, 45, 80)) -> bytes:
    """Generates an in-memory test image with specified dimensions and format."""
    img = Image.new("RGB", (width, height), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format=format, quality=85)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# 1. LocalStorageProvider Unit Tests
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_local_storage_provider_crud(tmp_path):
    """Test 1: LocalStorageProvider save, get, exists, and delete methods."""
    storage = LocalStorageProvider(base_directory=str(tmp_path), base_url="http://test/storage")

    file_bytes = b"Hello Wallpapers 8K1 Storage Engine!"
    rel_path = "subfolder/test_asset.txt"

    # 1. Save
    url = await storage.save(file_bytes, rel_path, "text/plain")
    assert url == "http://test/storage/subfolder/test_asset.txt"

    # 2. Exists
    assert await storage.exists(rel_path) is True

    # 3. Get
    retrieved = await storage.get(rel_path)
    assert retrieved == file_bytes

    # 4. Delete
    deleted = await storage.delete(rel_path)
    assert deleted is True
    assert await storage.exists(rel_path) is False


def test_local_storage_path_traversal_prevention(tmp_path):
    """Test 2: Prevents directory traversal attacks using invalid relative paths."""
    storage = LocalStorageProvider(base_directory=str(tmp_path))

    with pytest.raises(ValueError, match="Path traversal detected"):
        storage._resolve_safe_path("../../windows/system32/cmd.exe")

    with pytest.raises(ValueError, match="Path traversal detected"):
        storage._resolve_safe_path("..\\..\\secret.key")


# --------------------------------------------------------------------------
# 2. ImageProcessor Unit Tests
# --------------------------------------------------------------------------

def test_image_processor_8k_classification_and_variants():
    """Test 3: Processes 8K synthetic image into 4 multi-tier variants."""
    raw_8k = make_synthetic_image(7680, 4320, format="JPEG")
    result = ImageProcessor.process_image(raw_8k, filename="cosmic_space_8k.jpg")

    assert result.resolution == "8K"
    assert result.width == 7680
    assert result.height == 4320
    assert result.aspect_ratio == 1.7778
    assert result.file_format == "jpeg"
    assert result.original_extension == ".jpg"
    assert len(result.original_bytes) == len(raw_8k)

    # Verify Optimized variant: WebP with max dimension <= 3840
    opt_img = Image.open(io.BytesIO(result.optimized_bytes))
    assert opt_img.format == "WEBP"
    assert max(opt_img.width, opt_img.height) == 3840
    assert opt_img.width == 3840
    assert opt_img.height == 2160

    # Verify Preview variant: WebP with max dimension <= 1920
    prev_img = Image.open(io.BytesIO(result.preview_bytes))
    assert prev_img.format == "WEBP"
    assert max(prev_img.width, prev_img.height) == 1920
    assert prev_img.width == 1920
    assert prev_img.height == 1080

    # Verify Thumbnail variant: WebP with max dimension <= 600
    thumb_img = Image.open(io.BytesIO(result.thumbnail_bytes))
    assert thumb_img.format == "WEBP"
    assert max(thumb_img.width, thumb_img.height) == 600
    assert thumb_img.width == 600
    assert thumb_img.height == 337


def test_image_processor_resolution_classification():
    """Test 4: Accurate classification of 4K, 2K, FHD, and HD resolutions."""
    assert ImageProcessor.classify_resolution(3840, 2160) == "4K"
    assert ImageProcessor.classify_resolution(2560, 1440) == "2K"
    assert ImageProcessor.classify_resolution(1920, 1080) == "FHD"
    assert ImageProcessor.classify_resolution(1280, 720) == "HD"
    assert ImageProcessor.classify_resolution(800, 600) == "SD"


def test_image_processor_rejects_corrupted_file():
    """Test 5: Rejects corrupted/malicious bytes that fail Pillow header verification."""
    corrupted_bytes = b"GIF89a_NOT_A_REAL_IMAGE_DATA_PADDING_BYTES"
    with pytest.raises(BadRequestException) as exc_info:
        ImageProcessor.process_image(corrupted_bytes, filename="bad.jpg")
    assert exc_info.value.code == "INVALID_IMAGE_FILE"


def test_image_processor_rejects_empty_file():
    """Test 6: Rejects empty zero-byte uploads."""
    with pytest.raises(BadRequestException) as exc_info:
        ImageProcessor.process_image(b"", filename="empty.jpg")
    assert exc_info.value.code == "EMPTY_FILE"


# --------------------------------------------------------------------------
# 3. HTTP Upload Integration Tests
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_storage_upload_endpoint_admin_success(client: AsyncClient, admin_headers: dict):
    """Test 7: POST /api/v1/storage/upload processes image and returns 4 variant URLs."""
    img_bytes = make_synthetic_image(1920, 1080, format="PNG")
    files = {"file": ("test_upload.png", img_bytes, "image/png")}

    response = await client.post("/api/v1/storage/upload", files=files, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["success"] is True
    data = body["data"]

    # Verify URLs
    assert "original_url" in data
    assert "image_url" in data
    assert "thumbnail_url" in data
    assert "preview_url" in data

    assert data["original_url"].endswith(".png")
    assert data["image_url"].endswith("_optimized.webp")
    assert data["thumbnail_url"].endswith("_thumbnail.webp")
    assert data["preview_url"].endswith("_preview.webp")

    # Verify metadata
    assert data["width"] == 1920
    assert data["height"] == 1080
    assert data["aspect_ratio"] == 1.7778
    assert data["resolution"] == "FHD"
    assert data["file_format"] == "png"


@pytest.mark.asyncio
async def test_storage_upload_forbidden_for_regular_user(client: AsyncClient, user_headers: dict):
    """Test 8: POST /api/v1/storage/upload returns 403 FORBIDDEN_ROLE for non-admin user."""
    img_bytes = make_synthetic_image(800, 600, format="JPEG")
    files = {"file": ("user_upload.jpg", img_bytes, "image/jpeg")}

    response = await client.post("/api/v1/storage/upload", files=files, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["code"] == "FORBIDDEN_ROLE"


@pytest.mark.asyncio
async def test_wallpaper_upload_and_create_endpoint(client: AsyncClient, admin_headers: dict):
    """Test 9: POST /api/v1/wallpapers/upload uploads image and creates wallpaper in 1 step."""
    cat_resp = await client.get("/api/v1/categories")
    cat_id = cat_resp.json()["data"][0]["id"]
    uid = uuid.uuid4().hex[:6]

    img_bytes = make_synthetic_image(3840, 2160, format="JPEG")
    files = {"file": ("hypercar_8k.jpg", img_bytes, "image/jpeg")}
    form_data = {
        "title": f"Supercar Speed {uid}",
        "category_id": cat_id,
        "description": "High performance sports car in 4K resolution",
        "tags": "cars, supercars, fast, amoled",
        "is_featured": "true",
        "is_trending": "false",
        "is_daily": "false",
        "is_published": "true"
    }

    response = await client.post(
        "/api/v1/wallpapers/upload",
        files=files,
        data=form_data,
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["success"] is True
    wp = body["data"]

    assert wp["title"] == f"Supercar Speed {uid}"
    assert wp["resolution"] == "4K"
    assert wp["width"] == 3840
    assert wp["height"] == 2160
    assert wp["is_featured"] is True
    assert len(wp["tags"]) == 4

    # Verify queryable via standard GET
    get_resp = await client.get(f"/api/v1/wallpapers/{wp['id']}")
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["data"]["slug"] == wp["slug"]


@pytest.mark.asyncio
async def test_uploaded_file_accessible_via_static_files(client: AsyncClient, admin_headers: dict):
    """Test 10: Uploaded image file is retrievable over HTTP via StaticFiles mount."""
    img_bytes = make_synthetic_image(600, 400, format="JPEG", color=(200, 100, 50))
    files = {"file": ("static_test.jpg", img_bytes, "image/jpeg")}

    upload_resp = await client.post("/api/v1/storage/upload", files=files, headers=admin_headers)
    assert upload_resp.status_code == status.HTTP_201_CREATED
    thumb_url = upload_resp.json()["data"]["thumbnail_url"]

    # Extract relative path from thumb_url (e.g. /storage/uploads/wallpapers/...)
    path_suffix = thumb_url.split("/storage/uploads/")[-1]

    # Fetch through static files mount
    static_resp = await client.get(f"/storage/uploads/{path_suffix}")
    assert static_resp.status_code == status.HTTP_200_OK
    assert len(static_resp.content) > 0
    # Verify content is valid WebP
    loaded_img = Image.open(io.BytesIO(static_resp.content))
    assert loaded_img.format == "WEBP"
