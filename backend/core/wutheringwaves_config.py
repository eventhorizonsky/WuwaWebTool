from __future__ import annotations
"""Stub config for web version. Reads from backend/config.json or uses defaults."""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any


@dataclass
class ConfigItem:
    data: Any = None


class WutheringWavesConfig:
    """Web version of WutheringWavesConfig - reads from config.json."""
    _data: dict = {}

    @classmethod
    def _load(cls):
        if not cls._data:
            config_path = Path(__file__).parent.parent.parent / "config.json"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    cls._data = json.load(f)

    @classmethod
    def get_config(cls, key: str) -> ConfigItem:
        cls._load()
        return ConfigItem(data=cls._data.get(key))


# For web version: no proxy, no self-ck restriction
PREFIX = "ww"

class ShowConfig:
    """Stub for image.py CardBg config."""
    @staticmethod
    def get_config(key):
        from core.config import AppConfig
        return AppConfig.get_config(key)

