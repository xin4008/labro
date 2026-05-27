from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.deepseek import DeepSeekProvider
from app.config import AppSettings, get_settings


class StubAIProvider(AIProvider):
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise RuntimeError(
            "未配置 DeepSeek API 密钥。请在 backend/config.yaml 的 ai.api_key 中填写，"
            "或设置环境变量 DEEPSEEK_API_KEY。"
        )

    async def parse_literature(self, text: str, handout_text=None) -> dict:
        raise RuntimeError(
            "未配置 DeepSeek API 密钥。请在 backend/config.yaml 的 ai.api_key 中填写。"
        )

    async def refine_image_ocr_text(self, ocr_text: str, discipline=None, filename: str = "image") -> str:
        raise RuntimeError(
            "未配置 DeepSeek API 密钥。请在 backend/config.yaml 的 ai.api_key 中填写。"
        )


def get_ai_provider(settings: AppSettings | None = None) -> AIProvider:
    """统一返回 DeepSeek 提供商（仅此一家）。"""
    cfg = settings or get_settings()
    if not cfg.ai.api_key.strip():
        return StubAIProvider()
    return DeepSeekProvider(cfg.ai)
