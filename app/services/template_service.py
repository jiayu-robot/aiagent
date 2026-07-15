from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.core.errors import AppError
from app.domain.template_models import TemplateProfile


class TemplateService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_directories()

    @property
    def current_template_path(self) -> Path:
        return self.settings.persistent_templates_current_dir / "template.xlsx"

    @property
    def profile_path(self) -> Path:
        return self.settings.persistent_templates_current_dir / "profile.json"

    def save_current_template(self, upload_name: str, content: bytes) -> Path:
        if not upload_name.lower().endswith(".xlsx"):
            raise AppError("只支持 .xlsx Excel 模板文件")
        if len(content) > self.settings.max_excel_bytes:
            raise AppError("Excel 模板文件过大")

        self.settings.ensure_directories()
        if self.current_template_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            archive_path = self.settings.persistent_templates_history_dir / f"template-{timestamp}-{uuid4().hex[:8]}.xlsx"
            archive_path.write_bytes(self.current_template_path.read_bytes())

        self.current_template_path.write_bytes(content)
        return self.current_template_path

    def get_current_template(self) -> Path:
        if not self.current_template_path.exists():
            raise AppError("还没有上传当前 Excel 模板", status_code=404)
        return self.current_template_path

    def save_profile(self, profile: TemplateProfile) -> Path:
        self.settings.ensure_directories()
        self.profile_path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        return self.profile_path

    def load_profile(self) -> TemplateProfile:
        if not self.profile_path.exists():
            raise AppError("还没有保存模板字段映射", status_code=404)
        return TemplateProfile.model_validate_json(self.profile_path.read_text(encoding="utf-8"))
