from __future__ import annotations
from core.logger import logger

class DamageAttribute:
    pass

def getDamageAttribute():
    return DamageAttribute

def calc_percent_expression(*args, **kwargs):
    try:
        from ..waves_build.damage import calc_percent_expression as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return 0

def reload_damage_module():
    global DamageAttribute
    try:
        from ..waves_build.damage import DamageAttribute as d
        DamageAttribute = d
        globals()["DamageAttribute"] = d
    except ImportError:
        return None
    
def check_char_id(*args, **kwargs):
    try:
        from ..waves_build.damage import check_char_id as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return False