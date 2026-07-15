# AI Daily Report Assistant Design

## Goal

Build a local browser-based AI Daily Report Assistant for field engineers. The first version runs on Windows and Docker Compose, uses a deterministic Fake AI provider by default, saves one current Excel template and profile permanently, processes temporary photos and generated reports, and deletes temporary artifacts after 48 hours.

## Scope

Included in V1:

- FastAPI web app with simple HTML, CSS, and JavaScript.
- Upload and reuse one current `.xlsx` template.
- Inspect workbook sheets, non-empty cells, merged ranges, and existing images.
- Save a user-confirmed template profile with field mappings and photo slots.
- Accept Chinese work notes and multiple photos.
- Produce a validated `DailyReport` JSON preview with polished Chinese, English, timeline, work items, photo analyses, and warnings.
- Read photo EXIF datetime, apply EXIF orientation, and create compressed images.
- Keep AI and vision logic behind provider/service interfaces.
- Generate an Excel report from the current template without modifying the original template.
- Provide cleanup logic for temporary files older than 48 hours.
- Provide tests, Dockerfile, Compose file, and README.

Excluded from V1:

- Multi-agent orchestration, LangChain, Redis, Celery, PostgreSQL, SSO, public tunnel, mobile app, payments, Kubernetes, and fully automatic arbitrary Excel layout inference.

## Architecture

The app is a modular FastAPI project. API route modules handle HTTP parsing and response shaping only. Business logic lives in focused service modules. Pydantic v2 domain models define the stable internal report and template contracts, independent from any Excel workbook layout.

Persistent data lives under `data/persistent`: current template, profile, and terminology glossary. Temporary data lives under `data/temporary`: uploaded photos, processed images, job preview JSON, and generated reports. Cleanup only touches temporary directories.

## Components

- `app/main.py`: FastAPI app factory, web routes, static/template mounting, health endpoint, JSON error handling.
- `app/api/template_routes.py`: current template, upload, inspect, and profile APIs.
- `app/api/report_routes.py`: analyze, preview, generate, and download APIs.
- `app/core/config.py`: pydantic-settings configuration and filesystem paths.
- `app/domain/*.py`: `DailyReport`, `Timeline`, `WorkItem`, `MultilingualText`, `PhotoAnalysis`, `TemplateProfile`, `TemplateFieldMapping`, and `PhotoSlot`.
- `app/providers/*.py`: provider protocol, deterministic fake provider, and optional OpenAI provider.
- `app/services/template_service.py`: save, replace, reuse, and profile persistence.
- `app/services/template_inspector.py`: openpyxl workbook inspection.
- `app/services/glossary_service.py`: terminology JSON bootstrap and loading.
- `app/services/report_language_service.py`: convert raw Chinese notes into validated report content through a provider.
- `app/services/photo_service.py`: MIME/extension/size validation, safe filenames, EXIF, orientation, compression.
- `app/services/vision_service.py`: deterministic fake photo classification in V1.
- `app/services/report_validator.py`: timeline, related photo ID, low confidence, conflict, and template/profile validation.
- `app/services/excel_generator.py`: copy template, write mapped fields, insert images, return output path.
- `app/services/cleanup_service.py`: injectable-clock cleanup of only temporary paths.
- `app/services/report_workflow.py`: orchestrate analyze, preview persistence, preview update, and Excel generation.

## Data Flow

1. User uploads a template.
2. `TemplateService` validates `.xlsx`, archives any previous current template, saves the new current template, and returns inspection data.
3. User saves a `TemplateProfile` with mapped cells and photo slots.
4. User submits Chinese notes and photos.
5. `PhotoService` stores originals safely, reads EXIF datetime, corrects orientation, and writes compressed copies.
6. `ReportLanguageService` calls `FakeAIProvider` by default to produce deterministic structured text.
7. `VisionService` returns deterministic photo analyses and warnings.
8. `ReportWorkflow` validates and stores preview JSON under `data/temporary/jobs/<report_id>/preview.json`.
9. User edits preview fields in the browser.
10. `ExcelGenerator` copies the current template, writes mapped fields, inserts matching photos, and saves `Daily_Report_YYYYMMDD.xlsx`.
11. Download endpoint only serves files under `data/temporary/outputs`.
12. `CleanupService` deletes old temporary files while never touching persistent data, `.env`, or source code.

## Error Handling And Security

- User-visible API errors are JSON with Chinese messages.
- API keys are only read from environment variables.
- `.env` is ignored by git.
- Uploaded paths use generated safe names, never raw user filenames.
- Template uploads require `.xlsx`; image uploads require whitelisted extensions and MIME types.
- File sizes are limited by settings.
- Download paths are resolved and checked to stay under temporary outputs.
- Jinja templates escape user content by default; dynamic frontend insertion uses text fields and JSON.
- Logs do not include API keys or image contents.

## Testing

Default tests use `FakeAIProvider` and fake vision behavior. They do not call external AI APIs or require network access.

The suite covers template persistence, template replacement, inspection, profile serialization, glossary loading, Chinese-to-report conversion, EXIF reading, image rotation/compression, upload validation, timeline validation, low confidence warnings, conflict warnings, Excel cell writing, Excel image insertion, original template immutability, 48-hour cleanup, persistent-data protection, and an end-to-end API flow.

## Deployment

Local Python flow:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
fastapi dev app/main.py
```

Docker flow:

```powershell
docker compose up -d --build
```

The Dockerfile uses the official `python:3.12-slim` image, creates a non-root user, owns `/app/data`, and supports amd64/arm64 for Windows Docker Desktop and future Raspberry Pi 5 64-bit deployment.
