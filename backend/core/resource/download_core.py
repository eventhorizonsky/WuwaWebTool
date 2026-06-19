"""Download helpers using urllib (avoids aiohttp proxy issues)."""
from __future__ import annotations
import re
import asyncio
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from core.logger import logger

# Thread pool for blocking downloads
_executor = ThreadPoolExecutor(max_workers=8)
_ssl_ctx = ssl.create_default_context()

_DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def _parse_nginx_listing(html: str) -> list:
    """Parse nginx autoindex HTML, return list of filenames."""
    files = re.findall(r'href="([^"]+)"', html)
    return [f for f in files if f != "../" and not f.startswith("?") and not f.startswith("/")]


def _download_sync(url: str, dest: Path) -> bool:
    """Synchronous download (runs in thread pool). Skips if file already exists."""
    if dest.exists():
        return True  # Already downloaded, skip
    try:
        req = urllib.request.Request(url, headers=_DOWNLOAD_HEADERS)
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
            if resp.status != 200:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                f.write(resp.read())
            return True
    except Exception as e:
        logger.warning(f"Download error {url}: {e}")
        return False


def _fetch_text_sync(url: str) -> tuple:
    """Synchronous text fetch (runs in thread pool). Returns (status, content_type, body)."""
    try:
        req = urllib.request.Request(url, headers=_DOWNLOAD_HEADERS)
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
            ct = resp.headers.get("Content-Type", "")
            body = resp.read()
            return resp.status, ct, body
    except Exception as e:
        logger.warning(f"Fetch error {url}: {e}")
        return 0, "", b""


async def _download_directory(base_url: str, local_dir: Path, subpath: str = "") -> int:
    """Recursively download files from an nginx-served directory."""
    # IMPORTANT: trailing slash avoids nginx 301 redirect to 127.0.0.1:6566
    url = f"{base_url.rstrip('/')}/{subpath}/" if subpath else f"{base_url.rstrip('/')}/"
    local_dir.mkdir(parents=True, exist_ok=True)

    loop = asyncio.get_event_loop()

    status, content_type, body = await loop.run_in_executor(_executor, _fetch_text_sync, url)
    if status != 200:
        logger.warning(f"Failed to list {url}: HTTP {status}")
        return 0

    if "text/html" not in content_type:
        # Single file
        filename = subpath.split("/")[-1] if subpath else "index"
        dest = local_dir / filename
        ok = await loop.run_in_executor(_executor, _download_sync, url, dest)
        return 1 if ok else 0

    html = body.decode("utf-8", errors="replace")
    entries = _parse_nginx_listing(html)

    # Separate files and subdirectories
    files_to_dl = []
    dirs_to_dl = []
    for entry in entries:
        entry = entry.rstrip("/")
        if entry in ("../", "./"):
            continue
        last_part = entry.split("/")[-1] if "/" in entry else entry
        if "." not in last_part:
            dirs_to_dl.append(entry)
        else:
            files_to_dl.append(entry)

    # Download files concurrently
    tasks = []
    for entry in files_to_dl:
        file_url = f"{base_url.rstrip('/')}/{subpath}/{entry}" if subpath else f"{base_url.rstrip('/')}/{entry}"
        dest = local_dir / entry
        tasks.append(loop.run_in_executor(_executor, _download_sync, file_url, dest))

    # Recurse into subdirectories
    for entry in dirs_to_dl:
        entry_subpath = f"{subpath}/{entry}" if subpath else entry
        tasks.append(_download_directory(base_url, local_dir / entry, entry_subpath))

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return sum(r for r in results if isinstance(r, int))
    return 0


async def download_file(url: str, dest: Path) -> bool:
    """Download a single file."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _download_sync, url, dest)


async def download_all_file(plugin_name: str, resource_map: dict, base_url: str, tag: str) -> bool:
    """Download all resources from a mirror."""
    full_base = f"{base_url.rstrip('/')}/{plugin_name}"
    total_files = 0

    for remote_subpath, local_path in resource_map.items():
        logger.info(f"[资源下载] 开始: {tag} {remote_subpath}")
        count = await _download_directory(full_base, local_path, remote_subpath)
        if count > 0:
            logger.success(f"[资源下载] {tag} {remote_subpath} -> {local_path} ({count} files)")
            total_files += count
        else:
            logger.warning(f"[资源下载] 失败或为空: {tag} {remote_subpath}")

    return total_files > 0
