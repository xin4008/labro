import json
import re
from typing import Any, Dict, Optional

import httpx

from app.ai.base import AIProvider
from app.ai.http_client import build_http_client, friendly_connect_error
from app.ai.prompts import (
    build_image_ocr_refine_user_prompt,
    build_literature_user_prompt,
    get_image_ocr_refine_system,
    get_literature_parse_system,
)
from app.models.discipline import Discipline
from app.config import AISettings
from app.services.document_parser import truncate_text


class DeepSeekProvider(AIProvider):
    def __init__(self, settings: AISettings) -> None:
        self.settings = settings
        self.base_url = settings.base_url.rstrip("/")

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        url = f"{self.base_url}/v1/chat/completions"
        try:
            async with build_http_client(self.settings) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.settings.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise RuntimeError(friendly_connect_error(exc, self.base_url)) from exc

        if response.status_code != 200:
            detail = _extract_api_error(response)
            raise RuntimeError(
                f"DeepSeek API 调用失败 ({response.status_code})：{detail}"
            )
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("DeepSeek 返回格式异常") from exc

    async def parse_literature(
        self,
        text: str,
        handout_text: Optional[str] = None,
        discipline: Discipline = Discipline.CHEMISTRY,
    ) -> Dict[str, Any]:
        literature = truncate_text(text)
        handout = truncate_text(handout_text) if handout_text else None
        system_prompt = get_literature_parse_system(discipline)
        user_prompt = build_literature_user_prompt(literature, handout, discipline)
        raw = await self.complete(system_prompt, user_prompt)
        return _parse_json_response(raw)

    async def refine_image_ocr_text(
        self,
        ocr_text: str,
        discipline: Discipline = Discipline.CHEMISTRY,
        filename: str = "image",
    ) -> str:
        system_prompt = get_image_ocr_refine_system(discipline)
        user_prompt = build_image_ocr_refine_user_prompt(ocr_text, filename)
        return (await self.complete(system_prompt, user_prompt)).strip()


def _extract_api_error(response: httpx.Response) -> str:
    try:
        body = response.json()
        err = body.get("error") or {}
        if isinstance(err, dict) and err.get("message"):
            return str(err["message"])
        if isinstance(body.get("message"), str):
            return body["message"]
    except Exception:
        pass
    text = response.text.strip()
    return text[:300] if text else "未知错误，请检查 API 密钥与账户余额"


def _parse_json_response(raw: str) -> Dict[str, Any]:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI 返回的内容不是有效 JSON，请重试") from exc
    if not isinstance(data, dict):
        raise RuntimeError("AI 返回的 JSON 格式不正确")
    return data
