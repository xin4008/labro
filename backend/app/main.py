from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.config import BACKEND_ROOT, get_settings, resolve_path

FRONTEND_DIST = BACKEND_ROOT.parent / "frontend" / "dist"
from app.database import SessionLocal, init_db
from app.services.seed import seed_experiment_templates

WELCOME_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>化学实验助手 - 后端 API</title>
  <style>
    body { font-family: "Segoe UI", system-ui, sans-serif; max-width: 640px; margin: 48px auto; padding: 0 20px; color: #1e293b; line-height: 1.6; }
    h1 { color: #2563eb; font-size: 1.5rem; }
    .box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin: 20px 0; }
    a { color: #2563eb; }
    code { background: #e2e8f0; padding: 2px 8px; border-radius: 4px; }
    .warn { color: #b45309; font-size: 0.9rem; }
  </style>
</head>
<body>
  <h1>化学实验助手 · 后端 API 已运行</h1>
  <p class="warn">⚠ 这里是<strong>接口服务</strong>，不是应用界面。白屏 + prettyprint 说明您打开了 JSON 接口页。</p>
  <div class="box">
    <p><strong>请用浏览器打开前端页面：</strong></p>
    <p><a href="http://localhost:5173" target="_blank">http://localhost:5173</a></p>
    <p style="font-size:0.9rem;color:#64748b">需先在 <code>frontend</code> 目录运行 <code>npm run dev</code></p>
  </div>
  <p>开发者文档：<a href="/docs">/docs</a>（Swagger API 文档）</p>
  <p>健康检查：<a href="/api/health">/api/health</a></p>
</body>
</html>
"""


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_experiment_templates(db)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="化学实验助手 API",
        description="Chemistry Lab Assistant — MVP Backend",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/files/{experiment_id}/steps/{step_id}/{filename}", include_in_schema=False)
    def serve_step_image(experiment_id: str, step_id: int, filename: str):
        settings = get_settings()
        base = resolve_path(settings.storage.uploads_dir)
        path = base / experiment_id / "steps" / str(step_id) / Path(filename).name
        if not path.exists() or not path.is_file():
            raise HTTPException(status_code=404, detail="文件不存在")
        return FileResponse(path)

    app.include_router(api_router)

    if FRONTEND_DIST.is_dir():
        assets_dir = FRONTEND_DIST / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/", include_in_schema=False)
        def spa_index():
            return FileResponse(FRONTEND_DIST / "index.html")

        @app.get("/favicon.svg", include_in_schema=False)
        def spa_favicon():
            path = FRONTEND_DIST / "favicon.svg"
            if path.exists():
                return FileResponse(path)
            raise HTTPException(status_code=404)

        @app.get("/{page_path:path}", include_in_schema=False)
        def spa_routes(page_path: str):
            candidate = FRONTEND_DIST / page_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(FRONTEND_DIST / "index.html")
    else:

        @app.get("/", response_class=HTMLResponse, include_in_schema=False)
        def root() -> str:
            return WELCOME_HTML

    return app


app = create_app()
