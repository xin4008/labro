import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = BACKEND_ROOT / "config.yaml"
EXAMPLE_CONFIG_PATH = BACKEND_ROOT / "config.example.yaml"

# 统一 DeepSeek 配置（与 config.yaml 中 ai 段一致）
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"


class ServerSettings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )


class DatabaseSettings(BaseSettings):
    url: str = "sqlite:///./data/chemistry_lab.db"


class AISettings(BaseSettings):
    provider: str = "deepseek"
    api_key: str = ""
    base_url: str = DEEPSEEK_BASE_URL
    model: str = DEEPSEEK_MODEL
    timeout_seconds: int = 120
    # 无法直连时填写，例如 http://127.0.0.1:7890（Clash 等）
    proxy: str = ""


class SpeechSettings(BaseSettings):
    provider: str = "deepseek"
    api_key: str = ""
    base_url: str = DEEPSEEK_BASE_URL
    model: str = DEEPSEEK_MODEL


class StorageSettings(BaseSettings):
    uploads_dir: str = "./data/uploads"
    exports_dir: str = "./data/exports"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    server: ServerSettings = Field(default_factory=ServerSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ai: AISettings = Field(default_factory=AISettings)
    speech: SpeechSettings = Field(default_factory=SpeechSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)


def _load_yaml_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _apply_unified_deepseek(settings: AppSettings) -> None:
    """所有 AI 能力统一使用 DeepSeek 密钥与接口。"""
    env_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    yaml_key = (settings.ai.api_key or settings.speech.api_key or "").strip()
    api_key = env_key or yaml_key

    settings.ai.provider = "deepseek"
    settings.ai.api_key = api_key
    settings.ai.base_url = (settings.ai.base_url or DEEPSEEK_BASE_URL).rstrip("/")
    settings.ai.model = settings.ai.model or DEEPSEEK_MODEL

    settings.speech.provider = "deepseek"
    settings.speech.api_key = api_key
    settings.speech.base_url = settings.ai.base_url
    settings.speech.model = settings.ai.model or DEEPSEEK_MODEL


@lru_cache
def get_settings() -> AppSettings:
    config_path = DEFAULT_CONFIG_PATH if DEFAULT_CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH
    raw = _load_yaml_config(config_path)
    settings = AppSettings(**raw)
    _apply_unified_deepseek(settings)
    return settings


def get_deepseek_api_key() -> str:
    return get_settings().ai.api_key.strip()


def resolve_path(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute():
        return path
    return (BACKEND_ROOT / path).resolve()
