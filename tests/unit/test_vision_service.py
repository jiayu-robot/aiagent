from pathlib import Path

from app.domain.photo_models import ProcessedPhoto
from app.services.vision_service import VisionService


def photo(photo_id: str, filename: str, exif_datetime: str | None = None) -> ProcessedPhoto:
    return ProcessedPhoto(
        photo_id=photo_id,
        original_filename=filename,
        original_path=Path("original.jpg"),
        processed_path=Path("processed.jpg"),
        content_type="image/jpeg",
        exif_datetime=exif_datetime,
    )


def test_fake_vision_classifies_photos_deterministically():
    analyses = VisionService().analyze_photos(
        [
            photo("photo-1", "departure.jpg"),
            photo("photo-2", "site.jpg"),
            photo("photo-3", "hotel.jpg"),
        ]
    )

    assert [analysis.photo_type for analysis in analyses] == ["出发打卡", "工作现场", "到达酒店"]


def test_fake_vision_adds_low_confidence_warning():
    analysis = VisionService().analyze_photos([photo("photo-low", "low-confidence.jpg")])[0]

    assert analysis.confidence < 0.6
    assert "置信度较低" in analysis.warnings[0]


def test_fake_vision_adds_conflict_warning_when_visible_time_differs_from_exif():
    analysis = VisionService().analyze_photos(
        [photo("photo-conflict", "conflict.jpg", "2026:07:15 09:00:00")]
    )[0]

    assert analysis.visible_time == "10:00"
    assert any("EXIF 时间与画面时间不一致" in warning for warning in analysis.warnings)
