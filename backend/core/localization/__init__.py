from __future__ import annotations
import re
import json
from typing import Dict, List, Literal, Optional, Tuple, TypedDict

from core.logger import logger

from ..resource.RESOURCE_PATH import LOCALIZATION_PATH

Locale = Literal["cht", "en", "jp", "kr"]

_enabled = False
# 按 key 从长到短排序的列表，用于 partial 匹配时避免短 key 提前命中
_sorted_keys: List[str] = []

# 标点无关匹配：去标点后的 key -> 原始 key
_CJK_PUNCT_RE = re.compile(r'[，。！？；：、""''（）【】《》…—·～‧\s]')
_stripped_index: Dict[str, str] = {}
_stripped_keys: Dict[str, str] = {}


def _strip_punct(s: str) -> str:
    return _CJK_PUNCT_RE.sub('', s)


class LocaleEntry(TypedDict):
    cht: str
    en: str
    jp: str
    kr: str


LOCALIZATION: Dict[str, LocaleEntry] = {}


def _rebuild_sorted_keys() -> None:
    global _sorted_keys, _stripped_index, _stripped_keys
    _sorted_keys = sorted(LOCALIZATION.keys(), key=len, reverse=True)
    _stripped_index = {}
    _stripped_keys = {}
    for k in _sorted_keys:
        stripped = _strip_punct(k)
        _stripped_index.setdefault(stripped, k)
        _stripped_keys[k] = stripped


def _register(entries: Dict[str, LocaleEntry]) -> None:
    if _enabled:
        LOCALIZATION.update(entries)


def _load_i18n_json() -> None:
    """从 LOCALIZATION_PATH 加载所有 i18n JSON 文件"""
    if not LOCALIZATION_PATH.exists():
        return
    for f in LOCALIZATION_PATH.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            LOCALIZATION.update(data)
        except Exception:
            logger.exception(f"[鸣潮·本地化] 加载 {f.name} 失败")


def init_localization() -> None:
    """根据配置决定是否加载本地化字典，应在插件启动时调用"""
    global _enabled

    from ..wutheringwaves_config import WutheringWavesConfig
    _enabled = WutheringWavesConfig.get_config("EnableLocalization").data

    if _enabled:
        logger.info("[鸣潮·本地化] 已启用，开始加载翻译字典...")
        _load_i18n_json()
        # 导入各功能模块的翻译，触发注册
        from . import stamina  # noqa: F401
        from . import charinfo  # noqa: F401
        from . import stats  # noqa: F401
        _rebuild_sorted_keys()
        logger.info(f"[鸣潮·本地化] 加载完成，共 {len(LOCALIZATION)} 条翻译")
    else:
        LOCALIZATION.clear()
        _rebuild_sorted_keys()
        logger.info("[鸣潮·本地化] 未启用，跳过加载")


def t(text: str, locale: Optional[str], partial: bool = False) -> str:
    """将中文字符串转为目标语言的字符串。

    本地化未启用、locale 为空或 None 时原样返回。
    若字典中无对应条目，也原样返回。

    匹配时会同时尝试 key 的原版和去标点版，以忽略中文标点差异。
    partial=True 时，对 text 中所有匹配的子串进行替换（按 key 从长到短匹配）。
    """
    if not _enabled or not locale:
        return text
    if not partial:
        entry = LOCALIZATION.get(text)
        if entry is None:
            orig_key = _stripped_index.get(_strip_punct(text))
            if orig_key:
                entry = LOCALIZATION[orig_key]
        if entry is None:
            return text
        replacement = entry.get(locale)
        return replacement if replacement else text
    # partial 模式：逐个替换匹配到的子串
    result = text
    for key in _sorted_keys:
        entry = LOCALIZATION[key]
        replacement = entry.get(locale)
        if not replacement:
            continue
        if key in result:
            result = result.replace(key, replacement)
            continue
        # key 去标点后再试一次
        stripped = _stripped_keys.get(key, key)
        if stripped != key and stripped in result:
            result = result.replace(stripped, replacement)
    return result
