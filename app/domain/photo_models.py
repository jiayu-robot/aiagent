from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


PhotoType = Literal["出发打卡", "到达现场", "工作现场", "离开现场", "到达酒店", "其他"]


class ProcessedPhoto(BaseModel):
    photo_id: str
    original_filename: str
    original_path: Path
    processed_path: Path
    content_type: str
    exif_datetime: str | None = None


class PhotoAnalysis(BaseModel):
    photo_id: str
    original_filename: str
    exif_datetime: str | None = None
    visible_date: str | None = None
    visible_time: str | None = None
    visible_location: str | None = None
    photo_type: PhotoType
    description: str
    confidence: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)
