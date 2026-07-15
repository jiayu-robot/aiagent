from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_settings_create_required_data_directories(tmp_path):
    settings = Settings(app_data_root=tmp_path)

    settings.ensure_directories()

    assert settings.persistent_templates_current_dir.exists()
    assert settings.persistent_glossary_dir.exists()
    assert settings.temporary_jobs_dir.exists()
    assert settings.temporary_uploads_dir.exists()
    assert settings.temporary_processed_images_dir.exists()
    assert settings.temporary_outputs_dir.exists()


def test_health_endpoint_returns_ok(tmp_path):
    settings = Settings(app_data_root=tmp_path)
    app = create_app(settings)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
