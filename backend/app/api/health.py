import httpx
from fastapi import APIRouter

from app.ai.http_client import build_http_client, friendly_connect_error, resolve_proxy
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "phase": "4"}


@router.get("/ai-config")
def ai_config_status() -> dict:
    """检查 DeepSeek 是否已配置（不返回密钥）。"""
    settings = get_settings()
    proxy = resolve_proxy(settings.ai)
    return {
        "provider": "deepseek",
        "configured": bool(settings.ai.api_key),
        "base_url": settings.ai.base_url,
        "model": settings.ai.model,
        "proxy_configured": bool(proxy),
        "proxy_hint": "已启用代理" if proxy else "未配置代理（直连）",
    }


@router.post("/ai-test")
async def ai_connection_test() -> dict:
    """测试能否连上 DeepSeek（发送最小请求）。"""
    settings = get_settings()
    if not settings.ai.api_key:
        return {"ok": False, "message": "未配置 API 密钥"}

    url = f"{settings.ai.base_url.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": settings.ai.model,
        "messages": [{"role": "user", "content": "回复OK"}],
        "max_tokens": 5,
    }
    try:
        async with build_http_client(settings.ai) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.ai.api_key}"},
                json=payload,
                timeout=60.0,
            )
        if response.status_code == 200:
            return {"ok": True, "message": "DeepSeek 连接正常"}
        return {
            "ok": False,
            "message": f"HTTP {response.status_code}: {response.text[:200]}",
        }
    except httpx.HTTPError as exc:
        return {"ok": False, "message": friendly_connect_error(exc, settings.ai.base_url)}
