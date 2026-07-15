from app.core.config import Settings
from app.providers.fake_ai_provider import FakeAIProvider
from app.services.glossary_service import GlossaryService
from app.services.report_language_service import ReportLanguageService


def test_glossary_bootstraps_default_terms(tmp_path):
    service = GlossaryService(Settings(app_data_root=tmp_path))

    terms = service.load_terms()

    assert terms["主控"] == "Main Controller"
    assert terms["电池管理系统"] == "Battery Management System (BMS)"


def test_fake_provider_creates_deterministic_daily_report(tmp_path):
    glossary = GlossaryService(Settings(app_data_root=tmp_path)).load_terms()
    language_service = ReportLanguageService(FakeAIProvider(), glossary)

    report = language_service.create_report(
        raw_chinese="检查了一下主控，发现版本不一样，重新升级后正常了。",
        photo_ids=["photo-1", "photo-2"],
    )

    assert report.project_name == "现场工程项目"
    assert report.work_items[0].title_chinese == "主控系统检查"
    assert "主控系统的软件版本" in report.work_items[0].content.polished_chinese
    assert "Main Controller" in report.work_items[0].content.english
    assert report.work_items[0].related_photo_ids == ["photo-1", "photo-2"]
