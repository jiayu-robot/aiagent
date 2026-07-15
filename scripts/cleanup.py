import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.services.cleanup_service import CleanupService


def main() -> None:
    result = CleanupService(get_settings()).cleanup()
    print(f"Deleted {result.deleted_count} temporary item(s).")


if __name__ == "__main__":
    main()
