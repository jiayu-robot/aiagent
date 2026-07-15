import json
from pathlib import Path

from app.core.config import Settings
from app.core.errors import AppError
from app.domain.photo_models import ProcessedPhoto
from app.domain.report_models import DailyReport
from app.providers.fake_ai_provider import FakeAIProvider
from app.providers.openai_provider import OpenAIProvider
from app.services.excel_generator import ExcelGenerator
from app.services.glossary_service import GlossaryService
from app.services.photo_service import PhotoService
from app.services.report_language_service import ReportLanguageService
from app.services.report_validator import ReportValidator
from app.services.template_service import TemplateService
from app.services.vision_service import VisionService


class ReportWorkflow:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.template_service = TemplateService(settings)
        self.photo_service = PhotoService(settings)
        self.vision_service = VisionService()
        self.validator = ReportValidator()
        self.excel_generator = ExcelGenerator(settings)

    def analyze(self, raw_chinese: str, uploads: list[tuple[str, bytes, str]]) -> DailyReport:
        if not raw_chinese.strip():
            raise AppError("中文工作记录不能为空")
        photos = [self.photo_service.save_upload(name, content, content_type) for name, content, content_type in uploads]
        glossary = GlossaryService(self.settings).load_terms()
        provider = self._provider()
        report = ReportLanguageService(provider, glossary).create_report(
            raw_chinese=raw_chinese,
            photo_ids=[photo.photo_id for photo in photos],
        )
        report.photo_analyses = self.vision_service.analyze_photos(photos)
        profile = self.template_service.load_profile()
        template_path = self.template_service.get_current_template()
        self.validator.validate(report, profile, template_path)
        self._save_job(report, photos)
        return report

    def get_preview(self, report_id: str) -> DailyReport:
        preview_path = self._job_dir(report_id) / "preview.json"
        if not preview_path.exists():
            raise AppError("预览不存在或已被清理", status_code=404)
        return DailyReport.model_validate_json(preview_path.read_text(encoding="utf-8"))

    def generate_excel(self, report_id: str, report: DailyReport) -> Path:
        if report.report_id != report_id:
            raise AppError("日报 ID 不一致")
        profile = self.template_service.load_profile()
        template_path = self.template_service.get_current_template()
        self.validator.validate(report, profile, template_path)
        photos_by_id = self._load_photos(report_id)
        output_path = self.excel_generator.generate(template_path, profile, report, photos_by_id)
        self._save_job(report, self._load_processed_photos(report_id))
        return output_path

    def _provider(self):
        if self.settings.ai_provider == "openai":
            return OpenAIProvider(api_key=self.settings.openai_api_key, model=self.settings.openai_model)
        return FakeAIProvider()

    def _job_dir(self, report_id: str) -> Path:
        return self.settings.temporary_jobs_dir / report_id

    def _save_job(self, report: DailyReport, photos: list[ProcessedPhoto]) -> None:
        job_dir = self._job_dir(report.report_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "preview.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
        photo_data = [photo.model_dump(mode="json") for photo in photos]
        (job_dir / "photos.json").write_text(json.dumps(photo_data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_processed_photos(self, report_id: str) -> list[ProcessedPhoto]:
        photo_path = self._job_dir(report_id) / "photos.json"
        if not photo_path.exists():
            return []
        return [ProcessedPhoto.model_validate(item) for item in json.loads(photo_path.read_text(encoding="utf-8"))]

    def _load_photos(self, report_id: str) -> dict[str, Path]:
        return {photo.photo_id: photo.processed_path for photo in self._load_processed_photos(report_id)}
