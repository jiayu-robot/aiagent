from io import BytesIO

import pytest
from openpyxl import Workbook

from app.core.errors import AppError
from app.domain.photo_models import PhotoAnalysis
from app.domain.report_models import DailyReport, MultilingualText, Timeline, WorkItem
from app.domain.template_models import TemplateFieldMapping, TemplateProfile
from app.services.report_validator import ReportValidator


def report_with_times(**times: str | None) -> DailyReport:
    return DailyReport(
        report_id="report-1",
        report_date="2026-07-15",
        project_name="现场工程项目",
        timeline=Timeline(**times),
        work_items=[
            WorkItem(
                title_chinese="主控检查",
                title_english="Main Controller Inspection",
                content=MultilingualText(
                    raw_chinese="检查主控",
                    polished_chinese="检查主控系统。",
                    english="Checked the main controller system.",
                ),
                related_photo_ids=["photo-1"],
            )
        ],
        next_day_plan=MultilingualText(
            raw_chinese="继续测试",
            polished_chinese="继续测试。",
            english="Continue testing.",
        ),
    )


def minimal_profile() -> TemplateProfile:
    return TemplateProfile(
        template_filename="template.xlsx",
        fields={
            "report_date": TemplateFieldMapping(sheet_name="Daily", cell="B2"),
            "project_name": TemplateFieldMapping(sheet_name="Daily", cell="B3"),
            "work_content_chinese": TemplateFieldMapping(sheet_name="Daily", cell="B8", language="chinese"),
            "work_content_english": TemplateFieldMapping(sheet_name="Daily", cell="B9", language="english"),
        },
        photo_slots=[],
    )


def template_path(tmp_path):
    workbook = Workbook()
    workbook.active.title = "Daily"
    path = tmp_path / "template.xlsx"
    workbook.save(path)
    return path


def test_validator_rejects_invalid_time_order(tmp_path):
    report = report_with_times(departure_time="10:00", arrival_site_time="09:00")

    with pytest.raises(AppError, match="时间顺序"):
        ReportValidator().validate(report, minimal_profile(), template_path(tmp_path))


def test_validator_accepts_times_with_seconds(tmp_path):
    report = report_with_times(departure_time="08:44:00", arrival_site_time="15:39:00")
    report.photo_analyses = [
        PhotoAnalysis(photo_id="photo-1", original_filename="a.jpg", photo_type="工作现场", description="ok", confidence=0.9)
    ]

    warnings = ReportValidator().validate(report, minimal_profile(), template_path(tmp_path))

    assert warnings == []


def test_validator_rejects_unknown_related_photo_id(tmp_path):
    report = report_with_times(departure_time="08:00", arrival_site_time="09:00")

    with pytest.raises(AppError, match="不存在"):
        ReportValidator().validate(report, minimal_profile(), template_path(tmp_path))


def test_validator_adds_warning_for_low_confidence_and_conflict(tmp_path):
    report = report_with_times(departure_time="08:00", arrival_site_time="09:00")
    report.photo_analyses = [
        PhotoAnalysis(
            photo_id="photo-1",
            original_filename="conflict.jpg",
            exif_datetime="2026:07:15 09:00:00",
            visible_time="10:00",
            photo_type="工作现场",
            description="conflict",
            confidence=0.5,
        )
    ]

    warnings = ReportValidator().validate(report, minimal_profile(), template_path(tmp_path))

    assert any("置信度较低" in warning for warning in warnings)
    assert any("EXIF 时间与画面时间不一致" in warning for warning in warnings)


def test_validator_rejects_missing_required_profile_field(tmp_path):
    profile = TemplateProfile(template_filename="template.xlsx", fields={}, photo_slots=[])
    report = report_with_times(departure_time="08:00", arrival_site_time="09:00")
    report.photo_analyses = [
        PhotoAnalysis(photo_id="photo-1", original_filename="a.jpg", photo_type="工作现场", description="ok", confidence=0.9)
    ]

    with pytest.raises(AppError, match="缺少必需模板字段"):
        ReportValidator().validate(report, profile, template_path(tmp_path))
