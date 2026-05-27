import os
from typing import Optional

import httpx

from app.config import AISettings

# 连接阶段超时（秒）；读取仍用 timeout_seconds
CONNECT_TIMEOUT = 30.0


def resolve_proxy(settings: AISettings) -> Optional[str]:
    """
    仅使用 config.yaml 中显式配置的 proxy。
    不自动读取系统 HTTP_PROXY，避免错误代理导致 ConnectError。
    若 proxy 设为 \"env\"，才读取环境变量 HTTPS_PROXY。
    """
    proxy = str(getattr(settings, "proxy", None) or "").strip()
    if not proxy:
        return None
    if proxy.lower() == "env":
        return (
            os.getenv("HTTPS_PROXY")
            or os.getenv("https_proxy")
            or os.getenv("HTTP_PROXY")
            or os.getenv("http_proxy")
        )
    return proxy


def build_http_client(settings: AISettings) -> httpx.AsyncClient:
    timeout = httpx.Timeout(
        connect=CONNECT_TIMEOUT,
        read=float(settings.timeout_seconds),
        write=30.0,
        pool=10.0,
    )
    proxy = resolve_proxy(settings)
    kwargs: dict = {
        "timeout": timeout,
        "follow_redirects": True,
        # 关键：勿自动使用系统代理，除非在 config 里写明
        "trust_env": False,
    }
    if proxy:
        kwargs["proxy"] = proxy
    return httpx.AsyncClient(**kwargs)


def friendly_connect_error(exc: Exception, base_url: str) -> str:
    name = type(exc).__name__
    if "Connect" in name or "connect" in str(exc).lower():
        return (
            f"无法连接到 DeepSeek 服务器（{base_url}）。\n"
            "常见原因：① 本机未联网或校园网限制外网；② 防火墙/杀毒软件拦截；③ 需要代理/VPN。\n"
            "处理建议：① 若用 Clash 等，在 config.yaml 的 ai.proxy 填 http://127.0.0.1:7890 后重启后端；"
            "② 若已开代理仍失败，将 ai.proxy 留空并关闭错误的全局代理；"
            "③ 在浏览器测试能否打开 https://api.deepseek.com 。"
        )
    if "Timeout" in name:
        return "连接 DeepSeek 超时，请检查网络或增大 config.yaml 中的 timeout_seconds。"
    return str(exc).strip() or name
