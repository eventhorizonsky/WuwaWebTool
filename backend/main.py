"""WuwaWeb - FastAPI backend for Wuthering Waves character panel viewer."""
import sys
import os
from pathlib import Path

# Clear proxy environment variables (aiohttp may leak them despite trust_env=False)
for _key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "NO_PROXY"):
    os.environ.pop(_key, None)

# Ensure backend/ is on sys.path so "import core" works
sys.path.insert(0, str(Path(__file__).resolve().parent))

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.logger import logger

# Import API routers
from api.auth import router as auth_router
from api.game_data import router as game_data_router
from api.score import router as score_router
from login_pages import router as login_pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: download resources and initialize scoring engine."""
    logger.success("[WuwaWeb] 服务启动中...")

    # Initialize resource directories
    from core.resource.RESOURCE_PATH import init_dir
    init_dir()

    # Download resources from mirrors (waves_build, game data JSONs, images)
    try:
        from core.resource.download_all_resource import download_all_resource
        await download_all_resource(force=False)
        logger.success("[WuwaWeb] 资源下载完成")
    except Exception as e:
        logger.error(f"[WuwaWeb] 资源下载失败（将使用已有资源）: {e}")

    # Reload all scoring modules
    try:
        from core.resource.download_all_resource import reload_all_modules
        await reload_all_modules()
        logger.success("[WuwaWeb] 评分模块加载完成")
    except Exception as e:
        logger.error(f"[WuwaWeb] 评分模块加载失败: {e}")

    logger.success("[WuwaWeb] 服务就绪")

    yield

    logger.info("[WuwaWeb] 服务关闭")


app = FastAPI(
    title="WuwaWebTool",
    description="Wuthering Waves Character Panel Viewer",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend from any origin (configurable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(auth_router, prefix="/api/login", tags=["Auth"])
app.include_router(game_data_router, prefix="/api/game", tags=["Game Data"])
app.include_router(score_router, prefix="/api/score", tags=["Scoring"])

# Mount login pages
app.include_router(login_pages_router, tags=["Login Pages"])

# Image resource proxy - serve downloaded game resources (MUST be before frontend mount)
data_path = Path(__file__).resolve().parent / "data" / "XutheringWavesUID" / "resource"
if data_path.exists():
    app.mount("/static/resource", StaticFiles(directory=str(data_path)), name="resource")

# Mount static frontend files (mounted LAST because it catches all / paths)
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "wuwa-web"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
