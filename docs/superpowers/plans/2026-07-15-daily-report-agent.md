# AI Daily Report Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable local Web AI Daily Report Assistant on the Desktop with template upload/profile mapping, Fake AI report generation, photo handling, Excel generation, cleanup, tests, Docker Compose, README, and GitHub push.

**Architecture:** FastAPI routes stay thin and call service modules. Pydantic v2 domain models define template-independent report data. Persistent data stores the current Excel template, profile, and glossary; temporary data stores uploads, processed images, preview JSON, and generated reports.

**Tech Stack:** Python 3.12 target, FastAPI, Uvicorn/FastAPI CLI, Jinja2, Pydantic v2, pydantic-settings, openpyxl, Pillow, python-multipart, pytest, httpx, OpenAI Python SDK behind a provider interface, Docker, Docker Compose.

## Global Constraints

- Create project at `C:\Users\yangj\Desktop\daily-report-agent`.
- Save this plan at `docs/superpowers/plans/2026-07-15-daily-report-agent.md`.
- Use TDD: write failing tests before production code.
- Default tests must use Fake Provider and must not call real AI APIs.
- Business logic must not live in API routes.
- Do not implement multi-agent, LangChain, Redis, Celery, PostgreSQL, SSO, Cloudflare Tunnel, Cloudflare Pages, payments, mobile app, local LLM runtime, or arbitrary Excel auto-inference.
- Keep `data/persistent` permanent and only delete `data/temporary/jobs`, `data/temporary/uploads`, `data/temporary/processed_images`, and `data/temporary/outputs`.
- Docker must use an official multi-arch Python image and run as non-root.

---

## File Structure

- `app/main.py`: FastAPI app, web pages, static mounting, health endpoint, exception handler.
- `app/api/template_routes.py`: template upload/current/inspect/profile endpoints.
- `app/api/report_routes.py`: report analyze/preview/generate/download endpoints.
- `app/core/config.py`: settings and path creation.
- `app/core/errors.py`: safe app error class.
- `app/domain/report_models.py`: report and multilingual models.
- `app/domain/photo_models.py`: photo models and photo type literals.
- `app/domain/template_models.py`: template profile and inspection models.
- `app/providers/base_ai_provider.py`: provider protocol.
- `app/providers/fake_ai_provider.py`: deterministic fake provider.
- `app/providers/openai_provider.py`: optional OpenAI wrapper.
- `app/services/template_service.py`: template/profile persistence.
- `app/services/template_inspector.py`: workbook inspection.
- `app/services/glossary_service.py`: glossary bootstrap and load.
- `app/services/report_language_service.py`: provider-backed report creation.
- `app/services/photo_service.py`: image validation, EXIF, orientation, compression.
- `app/services/vision_service.py`: photo analysis interface and fake logic.
- `app/services/report_validator.py`: report/profile validation.
- `app/services/excel_generator.py`: Excel copy/write/image insertion.
- `app/services/cleanup_service.py`: 48-hour cleanup.
- `app/services/report_workflow.py`: analyze, preview, generate orchestration.
- `app/web/templates/*.html`: simple browser flow.
- `app/web/static/app.js` and `styles.css`: minimal frontend behavior.
- `scripts/cleanup.py`: CLI wrapper.
- `tests/unit/*.py`: module tests.
- `tests/integration/test_report_flow.py`: API end-to-end test.
- `tests/fixtures/`: generated small workbook and images.
- `.env.example`, `.gitignore`, `requirements.txt`, `Dockerfile`, `compose.yaml`, `README.md`: runtime and docs.

---

### Task 1: Project Initialization, Configuration, And Health

**Files:**
- Create: `.gitignore`, `.env.example`, `requirements.txt`, `app/__init__.py`, `app/main.py`, `app/core/config.py`, `app/core/errors.py`, `tests/conftest.py`, `tests/unit/test_health_and_config.py`

**Interfaces:**
- Produces: `Settings`, `get_settings()`, `create_app()`, `/health`.

- [ ] Write failing tests asserting data directories are created under a configurable root and `/health` returns `{"status": "ok"}`.
- [ ] Run `pytest tests/unit/test_health_and_config.py -q` and confirm failure because modules do not exist.
- [ ] Implement minimal settings, app factory, and health endpoint.
- [ ] Run the same test and confirm pass.
- [ ] Commit: `chore: initialize fastapi project`.

### Task 2: Domain Models

**Files:**
- Create: `app/domain/report_models.py`, `app/domain/photo_models.py`, `app/domain/template_models.py`, `tests/unit/test_domain_models.py`

**Interfaces:**
- Produces: `DailyReport`, `Timeline`, `WorkItem`, `MultilingualText`, `PhotoAnalysis`, `TemplateProfile`, `TemplateFieldMapping`, `PhotoSlot`.

- [ ] Write failing tests for model serialization, profile round-trip, valid photo type, and required field validation.
- [ ] Run `pytest tests/unit/test_domain_models.py -q` and confirm failure.
- [ ] Implement Pydantic v2 models with strict fields needed by later tasks.
- [ ] Run model tests and relevant health tests.
- [ ] Commit: `feat: add daily report domain models`.

### Task 3: Template Persistence And Inspection

**Files:**
- Create: `app/services/template_service.py`, `app/services/template_inspector.py`, `tests/unit/test_template_service.py`, `tests/unit/test_template_inspector.py`

**Interfaces:**
- Produces: `TemplateService.save_current_template(upload_name: str, content: bytes)`, `TemplateService.get_current_template()`, `TemplateService.save_profile(profile)`, `TemplateService.load_profile()`, `inspect_template(path)`.

- [ ] Write failing tests for saving a current template, replacing and archiving an old template, rejecting non-xlsx names, inspecting sheets/non-empty cells/merged ranges, and saving/loading profile JSON.
- [ ] Run the template tests and confirm failure.
- [ ] Implement service and inspector using `openpyxl`.
- [ ] Run template and domain tests.
- [ ] Commit: `feat: add template persistence and inspection`.

### Task 4: Glossary And Fake AI Report Language

**Files:**
- Create: `app/services/glossary_service.py`, `app/services/report_language_service.py`, `app/providers/base_ai_provider.py`, `app/providers/fake_ai_provider.py`, `app/providers/openai_provider.py`, `tests/unit/test_language_service.py`

**Interfaces:**
- Produces: `GlossaryService.load_terms()`, `ReportLanguageService.create_report(raw_chinese, photo_ids)`, `BaseAIProvider.create_daily_report(...)`.

- [ ] Write failing tests for default terminology bootstrap and deterministic Fake Provider output from Chinese input.
- [ ] Run language tests and confirm failure.
- [ ] Implement glossary loading and Fake AI provider with validated `DailyReport` output.
- [ ] Run language, domain, and config tests.
- [ ] Commit: `feat: add glossary and fake ai provider`.

### Task 5: Photo Processing And Vision

**Files:**
- Create: `app/services/photo_service.py`, `app/services/vision_service.py`, `tests/unit/test_photo_service.py`, `tests/unit/test_vision_service.py`

**Interfaces:**
- Produces: `PhotoService.save_upload(upload_name, content, content_type)`, `VisionService.analyze_photos(processed_photos)`.

- [ ] Write failing tests for MIME/extension/size validation, safe generated filenames, EXIF datetime reading, orientation/compression output, fake photo classification, low confidence warning, and visible/exif time conflict warning.
- [ ] Run photo and vision tests and confirm failure.
- [ ] Implement local image handling with Pillow and deterministic fake vision analysis.
- [ ] Run photo, vision, and prior unit tests.
- [ ] Commit: `feat: add photo processing and fake vision`.

### Task 6: Report Validation, Workflow, And Excel Generation

**Files:**
- Create: `app/services/report_validator.py`, `app/services/excel_generator.py`, `app/services/report_workflow.py`, `tests/unit/test_report_validator.py`, `tests/unit/test_excel_generator.py`

**Interfaces:**
- Produces: `ReportValidator.validate(report, profile, template_path)`, `ExcelGenerator.generate(report, profile, photos_by_id)`, `ReportWorkflow.analyze(...)`, `ReportWorkflow.generate_excel(...)`.

- [ ] Write failing tests for timeline ordering, missing required mapped fields, invalid related photo IDs, warnings for low confidence/conflict, Excel cell writes, image insertion, and original template immutability.
- [ ] Run workflow and Excel tests and confirm failure.
- [ ] Implement validator, workflow preview JSON persistence, and Excel generation.
- [ ] Run all unit tests.
- [ ] Commit: `feat: generate excel reports from previews`.

### Task 7: API And Web Flow

**Files:**
- Create: `app/api/template_routes.py`, `app/api/report_routes.py`, `app/web/templates/index.html`, `app/web/templates/template_setup.html`, `app/web/templates/report_preview.html`, `app/web/static/app.js`, `app/web/static/styles.css`, `tests/integration/test_report_flow.py`
- Modify: `app/main.py`

**Interfaces:**
- Produces: `GET /api/templates/current`, `POST /api/templates/upload`, `GET /api/templates/inspect`, `POST /api/templates/profile`, `POST /api/reports/analyze`, `GET /api/reports/{report_id}/preview`, `POST /api/reports/{report_id}/generate`, `GET /api/reports/{report_id}/download`.

- [ ] Write failing integration test for upload template, save profile, submit Chinese notes and two photos, receive preview, edit preview, generate Excel, download Excel, and verify output with `openpyxl`.
- [ ] Run integration test and confirm failure.
- [ ] Implement API routes and simple web pages.
- [ ] Run integration test and all unit tests.
- [ ] Commit: `feat: add web and report api flow`.

### Task 8: Cleanup, Docker, README, And Final Verification

**Files:**
- Create: `app/services/cleanup_service.py`, `scripts/cleanup.py`, `tests/unit/test_cleanup_service.py`, `Dockerfile`, `compose.yaml`, `README.md`

**Interfaces:**
- Produces: `CleanupService.cleanup()`, `python scripts/cleanup.py`, Docker Compose runtime.

- [ ] Write failing tests for deleting temporary files older than 48 hours and never deleting persistent template/glossary files.
- [ ] Run cleanup tests and confirm failure.
- [ ] Implement cleanup service and script.
- [ ] Add Dockerfile, compose file, and README with exact commands.
- [ ] Run `pytest -q`.
- [ ] Run `docker compose build`.
- [ ] Run `docker compose up -d`.
- [ ] Check `/health`.
- [ ] Run one end-to-end report generation test.
- [ ] Run `docker compose down`.
- [ ] Commit: `docs: add docker and operating guide`.

### Task 9: Push To GitHub

**Files:**
- All project files.

**Interfaces:**
- Remote: `https://github.com/jiayu-robot/aiagent.git`.

- [ ] Run `git status -sb`.
- [ ] Ensure all intended files are committed.
- [ ] Push `main` to `origin`.
- [ ] If authentication fails, report the exact push blocker and leave all local work committed.
