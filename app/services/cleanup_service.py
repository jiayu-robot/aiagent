import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from app.core.config import Settings


@dataclass(frozen=True)
class CleanupResult:
    deleted_count: int
    deleted_paths: list[str]


class CleanupService:
    def __init__(self, settings: Settings, now: Callable[[], datetime] | None = None) -> None:
        self.settings = settings
        self.settings.ensure_directories()
        self.now = now or (lambda: datetime.now(timezone.utc))

    def cleanup(self) -> CleanupResult:
        cutoff = self.now() - timedelta(hours=self.settings.temp_retention_hours)
        deleted: list[str] = []
        for root in self._temporary_roots():
            if not root.exists():
                continue
            for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
                if path == root or not path.exists():
                    continue
                mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                if mtime <= cutoff:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    deleted.append(str(path))
        return CleanupResult(deleted_count=len(deleted), deleted_paths=deleted)

    def _temporary_roots(self) -> tuple[Path, ...]:
        return (
            self.settings.temporary_jobs_dir,
            self.settings.temporary_uploads_dir,
            self.settings.temporary_processed_images_dir,
            self.settings.temporary_outputs_dir,
        )
