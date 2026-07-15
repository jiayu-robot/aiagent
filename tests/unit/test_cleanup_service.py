import os
from datetime import datetime, timedelta, timezone

from app.core.config import Settings
from app.services.cleanup_service import CleanupService


def set_mtime(path, when: datetime) -> None:
    timestamp = when.timestamp()
    os.utime(path, (timestamp, timestamp))


def test_cleanup_deletes_only_old_temporary_files(tmp_path):
    settings = Settings(app_data_root=tmp_path)
    settings.ensure_directories()
    now = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    old_file = settings.temporary_uploads_dir / "old.jpg"
    new_file = settings.temporary_uploads_dir / "new.jpg"
    old_file.write_text("old", encoding="utf-8")
    new_file.write_text("new", encoding="utf-8")
    set_mtime(old_file, now - timedelta(hours=49))
    set_mtime(new_file, now - timedelta(hours=1))

    result = CleanupService(settings, now=lambda: now).cleanup()

    assert old_file.exists() is False
    assert new_file.exists() is True
    assert result.deleted_count == 1


def test_cleanup_never_deletes_persistent_files(tmp_path):
    settings = Settings(app_data_root=tmp_path)
    settings.ensure_directories()
    now = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    persistent_file = settings.persistent_glossary_dir / "terminology.json"
    persistent_file.write_text("{}", encoding="utf-8")
    set_mtime(persistent_file, now - timedelta(days=10))

    CleanupService(settings, now=lambda: now).cleanup()

    assert persistent_file.exists() is True
