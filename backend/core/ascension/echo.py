from __future__ import annotations
from typing import Union, Optional

from msgspec import json as msgjson

from core.logger import logger

from .model import EchoModel
from ..resource.RESOURCE_PATH import MAP_DETAIL_PATH

MAP_PATH = MAP_DETAIL_PATH / "echo"
echo_id_data = {}
_data_loaded = False


def read_echo_json_files(directory):
    global echo_id_data
    files = directory.rglob("*.json")

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = msgjson.decode(f.read())
                file_name = file.name.split(".")[0]
                echo_id_data[file_name] = data
        except Exception as e:
            logger.exception(f"[鸣潮·声骸升级] read_echo_json_files load fail decoding {file}", e)


def ensure_data_loaded(force: bool = False):
    """确保声骸数据已加载

    Args:
        force: 如果为 True，强制重新加载所有数据，即使已经加载过
    """
    global _data_loaded
    if (_data_loaded and not force) or not MAP_PATH.exists():
        return
    read_echo_json_files(MAP_PATH)
    _data_loaded = True


def get_echo_model(echo_id: Union[int, str]) -> Optional[EchoModel]:
    ensure_data_loaded()
    if str(echo_id) not in echo_id_data:
        return None
    return EchoModel(**echo_id_data[str(echo_id)])
