from pydantic import BaseModel, ConfigDict

class ImageUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    original_url: str
    image_url: str
    thumbnail_url: str
    preview_url: str
    width: int
    height: int
    aspect_ratio: float
    file_size: int
    file_format: str
    resolution: str
