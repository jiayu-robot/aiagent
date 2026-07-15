from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.report_routes import router as report_router
from app.api.template_routes import router as template_router
from app.core.config import Settings, get_settings
from app.core.errors import AppError


WEB_DIR = Path(__file__).resolve().parent / "web"
templates = Jinja2Templates(directory=WEB_DIR / "templates")


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    active_settings.ensure_directories()

    app = FastAPI(title="AI Daily Report Assistant")
    app.state.settings = active_settings
    app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
    app.include_router(template_router)
    app.include_router(report_router)

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/template")
    def template_setup(request: Request):
        return templates.TemplateResponse("template_setup.html", {"request": request})

    @app.get("/preview/{report_id}")
    def report_preview(request: Request, report_id: str):
        return templates.TemplateResponse("report_preview.html", {"request": request, "report_id": report_id})

    return app


app = create_app()
