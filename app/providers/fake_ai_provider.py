from datetime import date
from uuid import uuid4

from app.domain.report_models import DailyReport, MultilingualText, Timeline, WorkItem


class FakeAIProvider:
    def create_daily_report(
        self,
        raw_chinese: str,
        glossary: dict[str, str],
        photo_ids: list[str],
    ) -> DailyReport:
        main_controller = glossary.get("主控", "Main Controller")
        polished = "检查主控系统的软件版本，发现当前版本存在不一致。随后完成主控软件升级，并确认升级后系统运行正常。"
        english = (
            f"Checked the software version of the {main_controller} and identified a version inconsistency. "
            "The main controller software was subsequently upgraded, and normal system operation was verified after the upgrade."
        )
        work_item = WorkItem(
            title_chinese="主控系统检查",
            title_english="Main Controller System Inspection",
            content=MultilingualText(raw_chinese=raw_chinese, polished_chinese=polished, english=english),
            related_photo_ids=photo_ids,
        )
        return DailyReport(
            report_id=f"report-{uuid4().hex}",
            report_date=date.today().isoformat(),
            project_name="现场工程项目",
            timeline=Timeline(
                departure_time="08:00",
                arrival_site_time="09:00",
                leave_site_time="17:00",
                arrival_hotel_time="18:00",
            ),
            work_items=[work_item],
            next_day_plan=MultilingualText(
                raw_chinese="继续现场检查和系统测试。",
                polished_chinese="继续开展现场检查，并完成后续系统测试工作。",
                english="Continue on-site inspection and complete follow-up system testing.",
            ),
            remarks="无",
            photo_analyses=[],
            warnings=[],
        )
