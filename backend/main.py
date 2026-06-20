"""WuwaWeb - FastAPI backend for Wuthering Waves character panel viewer."""
import sys
import os
from pathlib import Path

# Clear proxy environment variables (aiohttp may leak them despite trust_env=False)
for _key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "NO_PROXY"):
    os.environ.pop(_key, None)

# Ensure backend/ is on sys.path so "import core" works
sys.path.insert(0, str(Path(__file__).resolve().parent))

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.logger import logger

# Import API routers
from api.auth import router as auth_router
from api.game_data import router as game_data_router
from api.score import router as score_router
from login_pages import router as login_pages_router


def _print_env_config():
    """Print resolved configuration at startup."""
    from core.config import AppConfig

    def _cfg(key):
        return AppConfig.get_config(key).data

    data_path = os.environ.get("WUWA_DATA_PATH", "backend/data")
    port = os.environ.get("PORT", "8000")

    logger.info("=" * 50)
    logger.info("[WuwaWeb] 当前配置 (config.json + 环境变量覆盖)")
    logger.info(f"  PORT                      = {port}")
    logger.info(f"  WUWA_DATA_PATH            = {data_path}")
    logger.info(f"  LocalProxyUrl             = {_cfg('LocalProxyUrl') or '(直连)'}")
    logger.info(f"  NeedProxyFunc             = {_cfg('NeedProxyFunc') or '(无)'}")
    logger.info(f"  KuroUrlProxyUrl           = {_cfg('KuroUrlProxyUrl') or '(官方API)'}")
    logger.info(f"  CacheEverything           = {_cfg('CacheEverything')}")
    logger.info(f"  HideUid                   = {_cfg('HideUid')}")
    logger.info("=" * 50)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init dirs then download resources + load modules in the background.

    The HTTP server starts immediately and can respond to health checks
    while resource download runs asynchronously.  Scoring endpoints will
    return 503 until init completes.  This prevents cloud platforms (Render,
    Fly.io, etc.) from killing the container during the first download.
    """
    logger.success("[WuwaWeb] 服务启动中...")

    # Print resolved configuration
    _print_env_config()

    # Initialize resource directories (fast — just mkdir)
    from core.resource.RESOURCE_PATH import init_dir
    init_dir()

    # Track init state so /api/health and scoring endpoints can report it
    app.state.init_ready = False
    app.state.init_error = None

    async def _background_init():
        """Download resources & load scoring modules in background."""
        try:
            from core.resource.download_all_resource import (
                download_all_resource,
                reload_all_modules,
            )
            await download_all_resource(force=False)
            logger.success("[WuwaWeb] 资源下载完成")
            await reload_all_modules()
            logger.success("[WuwaWeb] 评分模块加载完成")
            app.state.init_ready = True
        except Exception as e:
            logger.error(f"[WuwaWeb] 初始化失败: {e}")
            app.state.init_error = str(e)

    bg_task = asyncio.create_task(_background_init())

    logger.success("[WuwaWeb] HTTP 服务就绪（资源后台下载中...）")

    yield

    # Shutdown
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass
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

@app.get("/api/health")
async def health(request: Request):
    """Health check — responds immediately even during background resource download."""
    return {
        "status": "ok",
        "service": "wuwa-web",
        "init_ready": request.app.state.init_ready,
        "init_error": request.app.state.init_error,
    }


# Mount login pages
app.include_router(login_pages_router, tags=["Login Pages"])

# Image resource proxy - serve downloaded game resources (MUST be before frontend mount)
data_path = Path(__file__).resolve().parent / "data" / "XutheringWavesUID" / "resource"
if data_path.exists():
    app.mount("/static/resource", StaticFiles(directory=str(data_path)), name="resource")

# Mount static frontend files (mounted LAST because it catches all / paths)
# In production, serve the Vite-built dist/ directory.
# Fall back to raw frontend/ if dist/ doesn't exist (e.g. during development without a build).
dist_path = Path(__file__).resolve().parent.parent / "frontend" / "dist"
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")
elif frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    import socket

    host = "::"
    port = int(os.environ.get("PORT", 8000))

    # Create a dual-stack socket that accepts both IPv4 and IPv6
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    sock.bind((host, port))

    uvicorn.run(
        "main:app",
        fd=sock.fileno(),
        forwarded_allow_ips="*",
    )
