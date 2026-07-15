from app.domain.report_models import DailyReport
from app.providers.base_ai_provider import BaseAIProvider


class ReportLanguageService:
    def __init__(self, provider: BaseAIProvider, glossary: dict[str, str]) -> None:
        self.provider = provider
        self.glossary = glossary

    def create_report(self, raw_chinese: str, photo_ids: list[str]) -> DailyReport:
        report = self.provider.create_daily_report(raw_chinese, self.glossary, photo_ids)
        return DailyReport.model_validate(report)
