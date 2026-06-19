from __future__ import annotations
from typing import Any, Dict, Tuple
from core.logger import logger

def calc_phantom_entry(*args, **kwargs) -> Tuple[float, float]:
    try:
        from .waves_build.calculate import calc_phantom_entry as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return 0, 0


def calc_phantom_score(*args, **kwargs) -> Tuple[float, str]:
    try:
        from .waves_build.calculate import calc_phantom_score as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return 0, "c"


def get_calc_map(*args, **kwargs) -> Dict:
    try:
        from .waves_build.calculate import get_calc_map as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return {}


def get_max_score(*args, **kwargs) -> Tuple[float, Any]:
    try:
        from .waves_build.calculate import get_max_score as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return 0, None


def get_total_score_bg(*args, **kwargs) -> str:
    try:
        from .waves_build.calculate import get_total_score_bg as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return "c"


def get_valid_color(*args, **kwargs) -> Tuple[str, str]:
    try:
        from .waves_build.calculate import get_valid_color as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return "#FFFFFF", "#FFFFFF"
