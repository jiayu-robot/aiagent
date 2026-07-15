from pydantic import BaseModel, Field

from app.domain.photo_models import PhotoAnalysis


class MultilingualText(BaseModel):
    raw_chinese: str = ""
    polished_chinese: str
    english: str


class Timeline(BaseModel):
    departure_time: str | None = None
    arrival_site_time: str | None = None
    leave_site_time: str | None = None
    arrival_hotel_time: str | None = None


class WorkItem(BaseModel):
    title_chinese: str
    title_english: str
    content: MultilingualText
    related_photo_ids: list[str] = Field(default_factory=list)


class DailyReport(BaseModel):
    report_id: str
    report_date: str
    project_name: str
    timeline: Timeline
    work_items: list[WorkItem]
    next_day_plan: MultilingualText
    remarks: str = ""
    photo_analyses: list[PhotoAnalysis] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    template_values: dict[str, str] = Field(default_factory=dict)
