from typing import Protocol

from app.domain.report_models import DailyReport


class BaseAIProvider(Protocol):
    def create_daily_report(
        self,
        raw_chinese: str,
        glossary: dict[str, str],
        photo_ids: list[str],
    ) -> DailyReport:
        """Create a validated report from Chinese notes."""
