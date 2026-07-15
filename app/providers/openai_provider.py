import json

from openai import OpenAI

from app.core.errors import AppError
from app.domain.report_models import DailyReport


class OpenAIProvider:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise AppError("未配置 OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def create_daily_report(
        self,
        raw_chinese: str,
        glossary: dict[str, str],
        photo_ids: list[str],
    ) -> DailyReport:
        prompt = (
            "将中文现场工程记录润色为专业中文并翻译为英文，返回 DailyReport JSON。"
            f"\n术语表: {json.dumps(glossary, ensure_ascii=False)}"
            f"\n照片ID: {photo_ids}"
            f"\n原始记录: {raw_chinese}"
        )
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return DailyReport.model_validate_json(response.output_text)
