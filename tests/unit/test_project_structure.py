from pathlib import Path


def test_expected_project_structure_exists():
    root = Path(__file__).resolve().parents[2]
    expected_paths = [
        "app/__init__.py",
        "app/main.py",
        "app/api/template_routes.py",
        "app/api/report_routes.py",
        "app/core/config.py",
        "app/core/errors.py",
        "app/core/logging_config.py",
        "app/domain/report_models.py",
        "app/domain/photo_models.py",
        "app/domain/template_models.py",
        "app/services/template_service.py",
        "app/services/template_inspector.py",
        "app/services/photo_service.py",
        "app/services/glossary_service.py",
        "app/services/report_language_service.py",
        "app/services/vision_service.py",
        "app/services/report_validator.py",
        "app/services/excel_generator.py",
        "app/services/cleanup_service.py",
        "app/services/report_workflow.py",
        "app/providers/base_ai_provider.py",
        "app/providers/openai_provider.py",
        "app/providers/fake_ai_provider.py",
        "app/web/templates/index.html",
        "app/web/templates/template_setup.html",
        "app/web/templates/report_preview.html",
        "app/web/static/app.js",
        "app/web/static/styles.css",
        "data/persistent/templates/current/.gitkeep",
        "data/persistent/glossary/.gitkeep",
        "data/temporary/jobs/.gitkeep",
        "data/temporary/uploads/.gitkeep",
        "data/temporary/processed_images/.gitkeep",
        "data/temporary/outputs/.gitkeep",
        "scripts/cleanup.py",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        ".env.example",
        ".gitignore",
        "requirements.txt",
        "Dockerfile",
        "compose.yaml",
        "README.md",
    ]

    missing = [path for path in expected_paths if not (root / path).exists()]

    assert missing == []
