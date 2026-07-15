from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_data_root: Path = Field(default=Path("data"))
    ai_provider: str = "fake"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    max_excel_bytes: int = 10 * 1024 * 1024
    max_image_bytes: int = 10 * 1024 * 1024
    temp_retention_hours: int = 48

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def persistent_dir(self) -> Path:
        return self.app_data_root / "persistent"

    @property
    def persistent_templates_dir(self) -> Path:
        return self.persistent_dir / "templates"

    @property
    def persistent_templates_current_dir(self) -> Path:
        return self.persistent_templates_dir / "current"

    @property
    def persistent_templates_history_dir(self) -> Path:
        return self.persistent_templates_dir / "history"

    @property
    def persistent_glossary_dir(self) -> Path:
        return self.persistent_dir / "glossary"

    @property
    def temporary_dir(self) -> Path:
        return self.app_data_root / "temporary"

    @property
    def temporary_jobs_dir(self) -> Path:
        return self.temporary_dir / "jobs"

    @property
    def temporary_uploads_dir(self) -> Path:
        return self.temporary_dir / "uploads"

    @property
    def temporary_processed_images_dir(self) -> Path:
        return self.temporary_dir / "processed_images"

    @property
    def temporary_outputs_dir(self) -> Path:
        return self.temporary_dir / "outputs"

    def ensure_directories(self) -> None:
        for directory in (
            self.persistent_templates_current_dir,
            self.persistent_templates_history_dir,
            self.persistent_glossary_dir,
            self.temporary_jobs_dir,
            self.temporary_uploads_dir,
            self.temporary_processed_images_dir,
            self.temporary_outputs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
