from io import BytesIO

import pytest
from openpyxl import Workbook

from app.core.config import Settings
from app.core.errors import AppError
from app.domain.template_models import TemplateFieldMapping, TemplateProfile
from app.services.template_service import TemplateService


def workbook_bytes(value: str = "日报模板") -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Daily"
    sheet["A1"] = value
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()


def test_save_current_template_and_reuse_it(tmp_path):
    settings = Settings(app_data_root=tmp_path)
    service = TemplateService(settings)

    saved = service.save_current_template("daily.xlsx", workbook_bytes())

    assert saved == settings.persistent_templates_current_dir / "template.xlsx"
    assert service.get_current_template() == saved


def test_replacing_template_archives_previous_current_template(tmp_path):
    settings = Settings(app_data_root=tmp_path)
    service = TemplateService(settings)
    service.save_current_template("daily.xlsx", workbook_bytes("old"))

    service.save_current_template("daily.xlsx", workbook_bytes("new"))

    archived = list(settings.persistent_templates_history_dir.glob("template-*.xlsx"))
    assert len(archived) == 1


def test_rejects_non_xlsx_template(tmp_path):
    service = TemplateService(Settings(app_data_root=tmp_path))

    with pytest.raises(AppError, match="只支持 .xlsx"):
        service.save_current_template("daily.xls", b"not xlsx")


def test_profile_round_trip(tmp_path):
    service = TemplateService(Settings(app_data_root=tmp_path))
    profile = TemplateProfile(
        template_filename="template.xlsx",
        fields={"report_date": TemplateFieldMapping(sheet_name="Daily", cell="B2")},
        photo_slots=[],
    )

    service.save_profile(profile)

    assert service.load_profile() == profile
