from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.models.discipline import Discipline


class AIProvider(ABC):
    """大模型提供商抽象接口。"""

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def parse_literature(
        self,
        text: str,
        handout_text: Optional[str] = None,
        discipline: Discipline = Discipline.CHEMISTRY,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def refine_image_ocr_text(
        self,
        ocr_text: str,
        discipline: Discipline = Discipline.CHEMISTRY,
        filename: str = "image",
    ) -> str:
        raise NotImplementedError
