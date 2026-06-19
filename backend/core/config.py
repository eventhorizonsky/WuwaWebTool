from __future__ import annotations
"""Configuration module — loads from config.json, Docker env vars take priority."""
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

# Env var → config key mapping (WUWA_* overrides config.json)
_ENV_MAP: dict[str, tuple[str, type]] = {
    "WUWA_KURO_URL_PROXY_URL": ("KuroUrlProxyUrl", str),
    "WUWA_LOCAL_PROXY_URL":   ("LocalProxyUrl",   str),
    "WUWA_NEED_PROXY_FUNC":   ("NeedProxyFunc",   list),   # comma-separated
    "WUWA_CACHE_EVERYTHING":  ("CacheEverything",  bool),
    "WUWA_HIDE_UID":          ("HideUid",          bool),
    "WUWA_PORT":              ("Port",             int),
}
# Aliases for common Docker conventions
_ENV_ALIASES: dict[str, str] = {
    "PORT": "WUWA_PORT",
}


@dataclass
class ConfigItem:
    data: Any = None


def _coerce(value: str, target_type: type) -> Any:
    if target_type is bool:
        return value.strip().lower() in ("1", "true", "yes", "on")
    if target_type is list:
        return [v.strip() for v in value.split(",") if v.strip()]
    if target_type is int:
        return int(value)
    return value


class AppConfig:
    """Config loaded from backend/config.json, with env var overrides."""

    _instance = None
    _data: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        # 1. Load config.json
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self._data = json.load(f)

        # 2. Override from environment variables (Docker-friendly)
        for env_key, (cfg_key, target_type) in _ENV_MAP.items():
            val = os.environ.get(env_key)
            if val is None and env_key in _ENV_ALIASES:
                val = os.environ.get(_ENV_ALIASES[env_key])
            if val is not None:
                self._data[cfg_key] = _coerce(val, target_type)

    @classmethod
    def get_config(cls, key: str) -> ConfigItem:
        inst = cls()
        return ConfigItem(data=inst._data.get(key))


# Global default config (no proxy by default)
def get_local_proxy_url():
    return AppConfig.get_config("LocalProxyUrl").data


def get_need_proxy_func():
    return AppConfig.get_config("NeedProxyFunc").data or []


# Default: use official API directly (no proxy)
KuroUrlProxyUrl = AppConfig.get_config("KuroUrlProxyUrl").data or None
