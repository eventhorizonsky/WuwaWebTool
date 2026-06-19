from __future__ import annotations
from typing import Optional

from core.logger import logger
from .error_reply import ERROR_CODE
from .wutheringwaves_config import PREFIX

BIND_UID_HINT = f"你还没有添加ck哦, 请使用 {PREFIX}添加CK 完成绑定！"

WAVES_ERROR_CODE = {}
WAVES_ERROR_CODE.update(ERROR_CODE)


def error_reply(code: Optional[int] = None, msg: str = "") -> str:
    msg_list = []
    if msg:
        msg_list.append(msg)
    elif code in WAVES_ERROR_CODE:
        msg_list.append(WAVES_ERROR_CODE[code])
    reply = "\n".join(msg_list)
    if isinstance(code, int):
        logger.error(f"[鸣潮·错误提示] ❌ 错误代码：{code} 📤 发送消息：{reply}")
    if msg:
        logger.error(f"[鸣潮·错误提示] 📝 错误信息：{msg}")
    return reply
