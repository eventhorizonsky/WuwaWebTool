from __future__ import annotations
import importlib
import re
from pathlib import Path

from core.logger import logger

from ...damage.abstract import DamageRankRegister, DamageDetailRegister, ScoreDetailRegister

# 漂泊者男女共用同一份伤害模块，需要把女性 ID 显式重定向到男性 ID 的模块上
ID_ALIASES = {
    "1408": "1406",
    "1501": "1502",
    "1605": "1604",
}

_SKIP_IDS = {"0000"}

_DAMAGE_FILE_RE = re.compile(r"^damage_(\d+)(?:\.|$)")


def _discover_id_mapping():
    waves_build_dir = Path(__file__).resolve().parent.parent / "waves_build"
    mapping = {}
    if waves_build_dir.is_dir():
        for entry in waves_build_dir.iterdir():
            if not entry.is_file():
                continue
            if entry.suffix not in (".py", ".so", ".pyd"):
                continue
            m = _DAMAGE_FILE_RE.match(entry.name)
            if not m:
                continue
            char_id = m.group(1)
            if char_id in _SKIP_IDS:
                continue
            mapping[char_id] = char_id
    mapping.update(ID_ALIASES)
    return mapping


ID_MAPPING = _discover_id_mapping()

# 一次完整 reload_all_register 里, 单个 damage_<id>.py 会被 register_damage /
# register_rank / register_score 各扫一遍, 加上 ID_MAPPING 里 1408→1406 / 1501→1502 /
# 1605→1604 这类别名共用模块, 不做去重会被 reload 多次, 触发 SQLModel 等的
# "类已存在" 警告。_reloaded_modules 在一次 reload_all_register 周期内共享, 保证
# 每个模块文件 reload 一次即可。
_INITIAL_IMPORT_NOTICE_SHOWN = False

def _dynamic_load_and_register(attr_name, register_cls, force_reload=False, reloaded_set=None):
    global _INITIAL_IMPORT_NOTICE_SHOWN, ID_MAPPING
    # 重新扫盘以兼容「首装时模块尚未下载完，下载完成后再 reload」的路径
    ID_MAPPING = _discover_id_mapping()
    current_globals = globals()
    if reloaded_set is None:
        reloaded_set = set()
    for char_id, module_suffix in ID_MAPPING.items():
        module_path = f"..waves_build.damage_{module_suffix}"
        try:
            module = importlib.import_module(module_path, package=__package__)
            if force_reload and module_suffix not in reloaded_set:
                # 编译扩展 (.so/.pyd) reload 行为不稳定, 仅 reload .py / .pyc。
                origin = ""
                spec = getattr(module, "__spec__", None)
                if spec is not None:
                    origin = getattr(spec, "origin", "") or ""
                if origin.endswith((".py", ".pyc")):
                    importlib.reload(module)
                else:
                    logger.debug(
                        f"[鸣潮·伤害注册] 跳过编译扩展 reload module={module_path} "
                        f"origin={origin}"
                    )
                reloaded_set.add(module_suffix)
            if not hasattr(module, attr_name):
                logger.debug(
                    f"[鸣潮·伤害注册] {module_path} 缺失 attr={attr_name} (char_id={char_id})"
                )
                continue

            target_obj = getattr(module, attr_name)
            if target_obj is None:
                continue
            if isinstance(target_obj, (list, dict)) and not target_obj:
                continue
            register_cls.register_class(char_id, target_obj)
            global_var_name = f"{attr_name.split('_')[0]}_{char_id}"
            current_globals[global_var_name] = target_obj

        except ImportError as e:
            if not _INITIAL_IMPORT_NOTICE_SHOWN and not force_reload:
                logger.warning(
                    "[鸣潮·伤害注册] 计算模块未找到，请观察下载是否进行，"
                    "并等待下载完成后再进行其他操作，除非遇到下载问题。"
                )
                _INITIAL_IMPORT_NOTICE_SHOWN = True
            logger.warning(
                f"[鸣潮·伤害注册] ImportError module={module_path} char_id={char_id} "
                f"attr={attr_name} reload={force_reload}: {e}"
            )
        except Exception as e:
            logger.warning(
                f"[鸣潮·伤害注册] {type(e).__name__} module={module_path} "
                f"char_id={char_id} attr={attr_name} reload={force_reload}: {e}"
            )


def register_damage(reload=False, reloaded_set=None):
    _dynamic_load_and_register(attr_name="damage_detail", register_cls=DamageDetailRegister, force_reload=reload, reloaded_set=reloaded_set)


def register_rank(reload=False, reloaded_set=None):
    _dynamic_load_and_register(attr_name="rank", register_cls=DamageRankRegister, force_reload=reload, reloaded_set=reloaded_set)


def register_score(reload=False, reloaded_set=None):
    _dynamic_load_and_register(attr_name="score_detail", register_cls=ScoreDetailRegister, force_reload=reload, reloaded_set=reloaded_set)


def reload_all_register():
    # 注册
    from ...queues import init_queues
    from ...damage.register_char import register_char
    from ...damage.register_echo import register_echo
    from ...damage.register_weapon import register_weapon

    register_weapon()
    register_echo()

    # 一个 cycle 内三个 register 共享 reloaded_set, 同一 damage_<id>.py 只 reload 一次
    reloaded_set = set()
    register_damage(reload=True, reloaded_set=reloaded_set)
    register_rank(reload=True, reloaded_set=reloaded_set)
    register_score(reload=True, reloaded_set=reloaded_set)

    register_char()

    # 初始化任务队列
    init_queues()
