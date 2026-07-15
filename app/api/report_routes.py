from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.errors import AppError
from app.domain.report_models import DailyReport
from app.services.report_workflow import ReportWorkflow


router = APIRouter(prefix="/api/reports", tags=["reports"])


class GeneratePayload(BaseModel):
    report: DailyReport


def _workflow(request: Request) -> ReportWorkflow:
    return ReportWorkflow(request.app.state.settings)


@router.post("/analyze")
async def analyze_report(
    request: Request,
    raw_chinese: str = Form(...),
    photos: list[UploadFile] = File(...),
) -> dict:
    uploads = []
    for photo in photos:
        uploads.append((photo.filename or "photo.jpg", await photo.read(), photo.content_type or "application/octet-stream"))
    report = _workflow(request).analyze(raw_chinese, uploads)
    return {"report_id": report.report_id, "report": report.model_dump()}


@router.get("/{report_id}/preview")
def preview_report(request: Request, report_id: str) -> dict:
    report = _workflow(request).get_preview(report_id)
    return {"report_id": report.report_id, "report": report.model_dump()}


@router.post("/{report_id}/generate")
def generate_report(request: Request, report_id: str, payload: GeneratePayload) -> dict:
    output_path = _workflow(request).generate_excel(report_id, payload.report)
    return {
        "status": "generated",
        "download_url": f"/api/reports/{report_id}/download",
        "filename": output_path.name,
        "expires_in_hours": request.app.state.settings.temp_retention_hours,
    }


@router.get("/{report_id}/download")
def download_report(request: Request, report_id: str) -> FileResponse:
    output_dir = (request.app.state.settings.temporary_outputs_dir / report_id).resolve()
    allowed_root = request.app.state.settings.temporary_outputs_dir.resolve()
    if allowed_root not in output_dir.parents and output_dir != allowed_root:
        raise AppError("下载路径不合法", status_code=403)
    files = sorted(Path(output_dir).glob("Daily_Report_*.xlsx"))
    if not files:
        raise AppError("日报文件不存在或已被清理", status_code=404)
    return FileResponse(
        files[-1],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=files[-1].name,
    )
