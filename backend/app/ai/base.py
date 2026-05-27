from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """大模型提供商抽象接口，Phase 2 实现具体解析逻辑。"""

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def parse_literature(self, text: str, handout_text: str | None = None) -> dict[str, Any]:
        raise NotImplementedError
