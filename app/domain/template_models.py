import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


Language = Literal["neutral", "chinese", "english"]


class TemplateFieldMapping(BaseModel):
    sheet_name: str
    cell: str
    language: Language = "neutral"
    optional: bool = False

    @field_validator("cell")
    @classmethod
    def validate_cell_reference(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Z]{1,3}[1-9][0-9]{0,6}", value.upper()):
            raise ValueError("invalid Excel cell reference")
        return value.upper()


class PhotoSlot(BaseModel):
    sheet_name: str
    anchor_cell: str
    width_px: int = Field(gt=0)
    height_px: int = Field(gt=0)
    accepted_photo_types: list[str] = Field(default_factory=list)

    @field_validator("anchor_cell")
    @classmethod
    def validate_anchor_cell(cls, value: str) -> str:
        return TemplateFieldMapping(sheet_name="_", cell=value).cell


class TemplateProfile(BaseModel):
    template_filename: str
    fields: dict[str, TemplateFieldMapping]
    photo_slots: list[PhotoSlot] = Field(default_factory=list)


class NonEmptyCell(BaseModel):
    sheet_name: str
    cell: str
    value: str


class TemplateInspection(BaseModel):
    sheets: list[str]
    non_empty_cells: list[NonEmptyCell]
    merged_ranges: dict[str, list[str]]
    image_counts: dict[str, int]
