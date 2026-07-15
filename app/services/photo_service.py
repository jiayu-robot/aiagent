from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps

from app.core.config import Settings
from app.core.errors import AppError
from app.domain.photo_models import ProcessedPhoto


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


class PhotoService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_directories()

    def save_upload(self, upload_name: str, content: bytes, content_type: str) -> ProcessedPhoto:
        suffix = Path(upload_name).suffix.lower()
        if content_type not in ALLOWED_IMAGE_TYPES or suffix not in ALLOWED_EXTENSIONS:
            raise AppError("只支持图片文件（JPG 或 PNG）")
        if len(content) > self.settings.max_image_bytes:
            raise AppError("图片文件过大")

        photo_id = f"photo-{uuid4().hex}"
        output_suffix = ".jpg" if content_type == "image/jpeg" else ".png"
        original_path = self.settings.temporary_uploads_dir / f"{photo_id}{output_suffix}"
        processed_path = self.settings.temporary_processed_images_dir / f"{photo_id}.jpg"
        original_path.write_bytes(content)

        with Image.open(original_path) as image:
            exif = image.getexif()
            exif_datetime = exif.get(36867) or exif.get(306)
            processed = ImageOps.exif_transpose(image)
            processed.thumbnail((1280, 1280))
            if processed.mode not in ("RGB", "L"):
                processed = processed.convert("RGB")
            processed.save(processed_path, format="JPEG", quality=82, optimize=True)

        return ProcessedPhoto(
            photo_id=photo_id,
            original_filename=upload_name,
            original_path=original_path,
            processed_path=processed_path,
            content_type=content_type,
            exif_datetime=str(exif_datetime) if exif_datetime else None,
        )
