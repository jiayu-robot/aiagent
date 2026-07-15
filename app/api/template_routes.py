from fastapi import APIRouter, Request, UploadFile

from app.domain.template_models import TemplateProfile
from app.services.template_inspector import inspect_template
from app.services.template_service import TemplateService


router = APIRouter(prefix="/api/templates", tags=["templates"])


def _service(request: Request) -> TemplateService:
    return TemplateService(request.app.state.settings)


@router.get("/current")
def current_template(request: Request) -> dict:
    service = _service(request)
    try:
        template_path = service.get_current_template()
        profile_exists = service.profile_path.exists()
        return {"exists": True, "template": template_path.name, "profile_exists": profile_exists}
    except Exception:
        return {"exists": False, "template": None, "profile_exists": False}


@router.post("/upload")
async def upload_template(request: Request, file: UploadFile) -> dict:
    service = _service(request)
    content = await file.read()
    template_path = service.save_current_template(file.filename or "template.xlsx", content)
    inspection = inspect_template(template_path)
    return {"status": "saved", "inspection": inspection.model_dump()}


@router.get("/inspect")
def inspect_current_template(request: Request) -> dict:
    service = _service(request)
    inspection = inspect_template(service.get_current_template())
    return {"inspection": inspection.model_dump()}


@router.post("/profile")
def save_profile(request: Request, profile: TemplateProfile) -> dict:
    _service(request).save_profile(profile)
    return {"status": "saved"}
