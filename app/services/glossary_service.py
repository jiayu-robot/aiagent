import json

from app.core.config import Settings


DEFAULT_TERMS = {
    "主控": "Main Controller",
    "电池管理系统": "Battery Management System (BMS)",
    "储能柜": "Battery Energy Storage Cabinet",
    "满充": "full charge",
    "满放": "full discharge",
    "一级报警": "Level 1 alarm",
    "二级报警": "Level 2 alarm",
    "气溶胶灭火系统": "aerosol fire suppression system",
    "容量测试": "capacity test",
    "充放电测试": "charge and discharge test",
}


class GlossaryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_directories()
        self.path = self.settings.persistent_glossary_dir / "terminology.json"

    def load_terms(self) -> dict[str, str]:
        if not self.path.exists():
            self.path.write_text(json.dumps(DEFAULT_TERMS, ensure_ascii=False, indent=2), encoding="utf-8")
        return json.loads(self.path.read_text(encoding="utf-8"))
