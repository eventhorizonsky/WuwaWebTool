from __future__ import annotations
from typing import Dict, List, Union, Optional

from msgspec import json as msgjson
from pydantic import Field, BaseModel

from core.logger import logger

from ..resource.RESOURCE_PATH import MAP_PATH, MAP_DETAIL_PATH

MAP_PATH_SONATA = MAP_DETAIL_PATH / "sonata"
SONATA_ID_MAP_PATH = MAP_PATH / "sonata_id.json"

sonata_id_data = {}
sonata_name_to_id = {}  # 中文名称 -> ID 映射
_data_loaded = False


def read_sonata_json_files(directory):
    global sonata_id_data
    files = directory.rglob("*.json")

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = msgjson.decode(f.read())
                file_name = file.name.split(".")[0]
                sonata_id_data[file_name] = data
        except Exception as e:
            logger.exception(f"[鸣潮·合鸣] read_char_json_files load fail decoding {file}", e)


def load_sonata_name_mapping():
    """加载 sonata_id.json 映射文件"""
    global sonata_name_to_id
    try:
        if SONATA_ID_MAP_PATH.exists():
            with open(SONATA_ID_MAP_PATH, "r", encoding="utf-8") as f:
                id_to_name = msgjson.decode(f.read())
                # 反向映射：名称 -> ID
                sonata_name_to_id = {v: k for k, v in id_to_name.items()}
        else:
            logger.warning(f"[鸣潮·合鸣] sonata_id.json not found at {SONATA_ID_MAP_PATH}")
    except Exception as e:
        logger.exception("[鸣潮·合鸣] Failed to load sonata_id.json mapping", e)


def ensure_data_loaded(force: bool = False):
    """确保合鸣数据已加载

    Args:
        force: 如果为 True，强制重新加载所有数据，即使已经加载过
    """
    global _data_loaded
    if (_data_loaded and not force) or not MAP_PATH_SONATA.exists():
        return
    read_sonata_json_files(MAP_PATH_SONATA)
    load_sonata_name_mapping()
    _data_loaded = True


class SonataSet(BaseModel):
    desc: str = Field(default="")
    effect: str = Field(default="")
    param: List[str] = Field(default_factory=list)


class WavesSonataResult(BaseModel):
    name: str = Field(default="")
    set: Dict[str, SonataSet] = Field(default_factory=dict)

    def piece(self, piece_count: Union[str, int]) -> Optional[SonataSet]:
        """获取件套效果"""
        return self.set.get(str(piece_count), None)

    def full_piece_effect(self) -> int:
        """获取套装最大件数"""
        return max(int(key) for key in self.set.keys())


def get_sonata_detail(sonata_name: Optional[str]) -> WavesSonataResult:
    ensure_data_loaded()
    result = WavesSonataResult()
    if sonata_name is None:
        logger.exception(f"[鸣潮·合鸣] get_sonata_detail sonata_name: {sonata_name} not found")
        return result

    sonata_key = str(sonata_name)

    # 如果输入的是中文名称，转换为ID
    if sonata_key not in sonata_id_data and sonata_key in sonata_name_to_id:
        sonata_key = sonata_name_to_id[sonata_key]

    if sonata_key not in sonata_id_data:
        logger.exception(f"[鸣潮·合鸣] get_sonata_detail sonata_name: {sonata_name} (converted to {sonata_key}) not found")
        return result

    return WavesSonataResult(**sonata_id_data[sonata_key])


# 组合套装规则: roleId -> 规则。某些角色(如洛可可)固定走 2+2 双套, 而非任一满件套。
# match 关键字命中套装"2 件效果"(effect/desc) 即为候选; 命中 need 个各 >= pieces 件即成立。
# 候选套装从 sonata 数据动态发现, 新增套装写进数据即自动纳入。
COMBO_SONATA_RULES: Dict[int, Dict] = {
    1606: {"label": "洛2+2", "match": ["湮灭", "攻击"], "pieces": 2, "need": 2},  # 洛可可
    1506: {"label": "菲2+2", "match": ["衍射", "攻击"], "pieces": 2, "need": 2},  # 菲比
}


def get_2pc_sonata_names(keywords: List[str]) -> List[str]:
    """返回具备 2 件效果、且 2 件 effect/desc 命中任一关键字的套装名 (排除 3 件/1 件套)。"""
    ensure_data_loaded()
    names = []
    for data in sonata_id_data.values():
        two = (data.get("set") or {}).get("2")
        if not two:
            continue
        text = f"{two.get('effect', '')}{two.get('desc', '')}"
        if any(k in text for k in keywords):
            name = data.get("name")
            if name:
                names.append(name)
    return names


def detect_combo_sonata(role_id: Union[int, str], ph_detail: List[Dict]) -> Optional[str]:
    """命中组合套装规则返回 '标签|套装A|套装B', 否则 None。"""
    try:
        rule = COMBO_SONATA_RULES.get(int(role_id))
    except (TypeError, ValueError):
        rule = None
    if not rule:
        return None
    candidates = set(get_2pc_sonata_names(rule["match"]))
    if not candidates:
        return None
    need_pieces = rule.get("pieces", 2)
    matched: List[str] = []
    for pd in ph_detail:
        name = pd.get("ph_name")
        if name in candidates and pd.get("ph_num", 0) >= need_pieces and name not in matched:
            matched.append(name)
    if len(matched) >= rule.get("need", 2):
        return rule["label"] + "|" + "|".join(matched[: rule["need"]])
    return None
