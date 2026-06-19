from core.logger import logger

def check_if_ph_3(*args, **kwargs) -> bool:
    try:
        from ..waves_build.damage import check_if_ph_3 as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return False


def check_if_ph_5(*args, **kwargs) -> bool:
    try:
        from ..waves_build.damage import check_if_ph_5 as _func
        return _func(*args, **kwargs)
    except ImportError:
        logger.info("[鸣潮·伤害计算] 请等待下载完成")
        return False
