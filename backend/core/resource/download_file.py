from __future__ import annotations
from typing import Union

from PIL import Image

# Replace gsuid_core download with our local implementation
async def _download(url: str, dest_dir, name: str, tag: str = "") -> bool:
    from .download_core import download_file as _dl
    from pathlib import Path
    d = Path(dest_dir)
    d.mkdir(parents=True, exist_ok=True)
    return await _dl(url, d / name)

from .RESOURCE_PATH import (
    PHANTOM_PATH,
    MATERIAL_PATH,
    ROLE_DETAIL_SKILL_PATH,
    ROLE_DETAIL_CHAINS_PATH,
)


async def get_skill_img(char_id: Union[str, int], skill_name: str, pic_url: str) -> Image.Image:
    _dir = ROLE_DETAIL_SKILL_PATH / str(char_id)
    _dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_name.strip()
    name = f"skill_{skill_name}.png"
    _path = _dir / name
    if not _path.exists():
        if pic_url:
            await _download(pic_url, _dir, name, tag="[鸣潮]")
        else:
            # logger.warning(f"[鸣潮·资源下载] 角色 {char_id} 的技能图片不存在，使用默认图片")
            _path = ROLE_DETAIL_SKILL_PATH / "1503" / "skill_星星花绽放.png"

    return Image.open(_path).convert("RGBA")


async def get_chain_img(char_id: Union[str, int], order_id: int, pic_url: str) -> Image.Image:
    _dir = ROLE_DETAIL_CHAINS_PATH / str(char_id)
    _dir.mkdir(parents=True, exist_ok=True)

    name = f"chain_{order_id}.png"
    _path = _dir / name
    if not _path.exists():
        if pic_url:
            await _download(pic_url, _dir, name, tag="[鸣潮]")
        else:
            # logger.warning(f"[鸣潮·资源下载] 角色 {char_id} 的共鸣链图片不存在，使用默认图片")
            _path = ROLE_DETAIL_CHAINS_PATH / "1503" / f"chain_{order_id}.png"

    return Image.open(_path).convert("RGBA")


async def get_phantom_img(phantom_id: int, pic_url: str) -> Image.Image:
    name = f"phantom_{phantom_id}.png"
    _path = PHANTOM_PATH / name
    if not _path.exists():
        if pic_url:
            await _download(pic_url, PHANTOM_PATH, name, tag="[鸣潮]")
        else:
            _path = PHANTOM_PATH / "phantom_390070051.png"

    return Image.open(_path).convert("RGBA")


async def get_material_img(material_id: Union[str, int]) -> Image.Image:
    name = f"material_{material_id}.png"
    _path = MATERIAL_PATH / name
    return Image.open(_path).convert("RGBA")
