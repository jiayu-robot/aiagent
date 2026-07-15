import pytest
from pydantic import ValidationError

from app.domain.photo_models import PhotoAnalysis
from app.domain.report_models import DailyReport, MultilingualText, Timeline, WorkItem
from app.domain.template_models import PhotoSlot, TemplateFieldMapping, TemplateProfile


def test_daily_report_serializes_core_fields():
    report = DailyReport(
        report_id="report-1",
        report_date="2026-07-15",
        project_name="储能项目",
        timeline=Timeline(departure_time="08:00", arrival_site_time="09:00"),
        work_items=[
            WorkItem(
                title_chinese="主控检查",
                title_english="Main Controller Inspection",
                content=MultilingualText(
                    raw_chinese="检查主控",
                    polished_chinese="检查主控系统的软件版本。",
                    english="Checked the software version of the main control system.",
                ),
                related_photo_ids=["photo-1"],
            )
        ],
        next_day_plan=MultilingualText(
            raw_chinese="继续测试",
            polished_chinese="继续开展系统测试。",
            english="Continue system testing.",
        ),
        remarks="无",
        photo_analyses=[],
        warnings=[],
    )

    dumped = report.model_dump()

    assert dumped["timeline"]["departure_time"] == "08:00"
    assert dumped["work_items"][0]["content"]["english"].startswith("Checked")


def test_template_profile_round_trip_preserves_mappings():
    profile = TemplateProfile(
        template_filename="template.xlsx",
        fields={
            "report_date": TemplateFieldMapping(sheet_name="Daily", cell="B2", language="neutral"),
            "work_content_english": TemplateFieldMapping(sheet_name="Daily", cell="B8", language="english"),
        },
        photo_slots=[
            PhotoSlot(
                sheet_name="Daily",
                anchor_cell="A12",
                width_px=320,
                height_px=240,
                accepted_photo_types=["工作现场"],
            )
        ],
    )

    loaded = TemplateProfile.model_validate_json(profile.model_dump_json())

    assert loaded.fields["work_content_english"].language == "english"
    assert loaded.photo_slots[0].accepted_photo_types == ["工作现场"]


def test_photo_analysis_rejects_unknown_photo_type():
    with pytest.raises(ValidationError):
        PhotoAnalysis(
            photo_id="photo-1",
            original_filename="site.jpg",
            photo_type="未知类型",
            description="invalid",
            confidence=0.9,
        )


def test_template_field_requires_valid_cell_reference():
    with pytest.raises(ValidationError):
        TemplateFieldMapping(sheet_name="Daily", cell="not-a-cell", language="neutral")
