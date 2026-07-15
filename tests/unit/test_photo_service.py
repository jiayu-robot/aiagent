from io import BytesIO

import pytest
from PIL import Image

from app.core.config import Settings
from app.core.errors import AppError
from app.services.photo_service import PhotoService


def jpeg_bytes(with_exif: bool = True, orientation: int | None = None) -> bytes:
    image = Image.new("RGB", (20, 40), color="navy")
    stream = BytesIO()
    exif = Image.Exif()
    if with_exif:
        exif[36867] = "2026:07:15 09:30:00"
    if orientation is not None:
        exif[274] = orientation
    image.save(stream, format="JPEG", exif=exif)
    return stream.getvalue()


def test_save_upload_reads_exif_and_generates_safe_paths(tmp_path):
    service = PhotoService(Settings(app_data_root=tmp_path))

    photo = service.save_upload("现场照片.jpg", jpeg_bytes(), "image/jpeg")

    assert photo.exif_datetime == "2026:07:15 09:30:00"
    assert photo.original_path.exists()
    assert photo.processed_path.exists()
    assert "现场照片" not in photo.original_path.name
    assert photo.processed_path.suffix == ".jpg"


def test_save_upload_applies_orientation_and_compresses(tmp_path):
    service = PhotoService(Settings(app_data_root=tmp_path))

    photo = service.save_upload("rotate.jpg", jpeg_bytes(orientation=6), "image/jpeg")

    with Image.open(photo.processed_path) as processed:
        assert processed.size == (40, 20)


def test_save_upload_rejects_invalid_content_type(tmp_path):
    service = PhotoService(Settings(app_data_root=tmp_path))

    with pytest.raises(AppError, match="只支持图片"):
        service.save_upload("note.txt", b"hello", "text/plain")


def test_save_upload_rejects_oversized_image(tmp_path):
    settings = Settings(app_data_root=tmp_path, max_image_bytes=5)
    service = PhotoService(settings)

    with pytest.raises(AppError, match="图片文件过大"):
        service.save_upload("site.jpg", jpeg_bytes(), "image/jpeg")
