from __future__ import annotations
from typing import Any, Dict, List, Tuple, Union, Optional

from pydantic import Field, BaseModel

from ..util import format_with_defaults, _collapse_repeated_slash_values
from ..resource.constant import ATTRIBUTE_ID_MAP


class Stats(BaseModel):
    life: float
    atk: float
    def_: float = Field(..., alias="def")  # `def` is a reserved keyword, use `def_`


class WeaponStats(BaseModel):
    name: str
    value: Union[str, float]
    isRatio: bool
    isPercent: bool


class LevelExp(BaseModel):
    level: int
    exp: int


class SkillLevel(BaseModel):
    name: str
    param: List[List[str]]
    format: Optional[str] = None


class Skill(BaseModel):
    name: str
    desc: str
    param: List[str]
    type: Optional[str] = None
    level: Optional[Dict[str, SkillLevel]] = None

    def get_desc_detail(self):
        return format_with_defaults(self.desc, self.param)


class SkillBranchItem(BaseModel):
    name: str
    desc: str
    isDefault: bool = False


class Chain(BaseModel):
    name: str
    desc: str
    param: List[Union[str, float]]

    def get_desc_detail(self):
        return format_with_defaults(self.desc, self.param)


class AscensionMaterial(BaseModel):
    key: int
    value: int


class StatsWeakness(BaseModel):
    weaknessBuildUp: int
    weaknessBuildUpMax: int
    weaknessTotalBonus: int
    breakWeaknessRatio: int
    weaknessMastery: int


class CharacterModel(BaseModel):
    name: str
    starLevel: int
    attributeId: int
    weaponTypeId: int
    stats: Dict[str, Dict[str, Stats]]
    skillTree: Dict[str, Dict[str, Skill]]
    chains: Dict[int, Chain]
    ascensions: Dict[str, List[AscensionMaterial]]
    skillBranches: Optional[List[SkillBranchItem]] = None
    statsWeakness: Optional[StatsWeakness] = None

    class Config:
        # Updated configuration keys for Pydantic v2
        populate_by_name = True  # Replaces `allow_population_by_field_name`
        str_strip_whitespace = True  # Replaces `anystr_strip_whitespace`

    def get_max_level_stat(self) -> Stats:
        return self.stats["6"]["90"]

    def get_attribute_name(self) -> str:
        return ATTRIBUTE_ID_MAP[self.attributeId]

    def get_ascensions_max_list(self) -> list:
        """获取最高等级突破材料ID列表（排除贝币 ID=2）"""
        for i in ["6", "5", "4", "3", "2"]:
            try:
                value = [j.key for j in self.ascensions[i] if j.key != 2]
                if value:
                    return value
            except Exception:
                continue
        return []


class WeaponModel(BaseModel):
    name: str
    type: int
    starLevel: int
    stats: Dict[str, Dict[str, List[WeaponStats]]]
    effect: str
    effectName: str
    param: List[List[str]]
    desc: str
    ascensions: Dict[str, List[AscensionMaterial]]

    class Config:
        # Updated configuration keys for Pydantic v2
        populate_by_name = True  # Replaces `allow_population_by_field_name`
        str_strip_whitespace = True  # Replaces `anystr_strip_whitespace`
        str_min_length = 1  # Replaces `min_anystr_length`

    def get_max_level_stat_tuple(self) -> List[Tuple[str, str]]:
        stats = self.stats["6"]["90"]
        rets = []
        for stat in stats:
            if stat.isPercent:
                ret = f"{float(stat.value) / 100:.1f}%"
            elif stat.isRatio:
                ret = f"{stat.value * 100:.1f}%"
            else:
                ret = f"{int(stat.value)}"
            rets.append((stat.name, ret))

        return rets

    def get_effect_detail(self):
        result = self.effect.format(*["(" + "/".join(i) + ")" if len(set(i)) > 1 else i[0] for i in self.param])
        return _collapse_repeated_slash_values(result)

    def get_ascensions_max_list(self):
        for i in ["5", "4", "3", "2"]:
            try:
                value = [j.key for j in self.ascensions[i]]
                # 加入贝币(ID=2)凑齐3件
                if 2 not in value:
                    value.append(2)
                return value
            except Exception:
                continue
        return []

    def get_weapon_type(self) -> str:
        weapon_type = {
            1: "长刃",
            2: "迅刀",
            3: "佩枪",
            4: "臂铠",
            5: "音感仪",
        }
        return weapon_type.get(self.type, "")


class EchoModel(BaseModel):
    id: int
    name: str
    intensityCode: int
    group: Dict[str, Dict[str, str]]
    skill: Dict[str, Any]
    resistance: Dict[str, float] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        str_strip_whitespace = True
        str_min_length = 1

    def get_skill_detail(self):
        return format_with_defaults(self.skill["desc"], self.skill["params"][-1])

    def get_resistance(self) -> List[Dict[str, Any]]:
        """声骸(怪物)抗性 → [{name, value, hi}]; 高于基础 10 的标记 hi; 无数据返回 []。"""
        name_map = [
            ("phys", "物理"), ("glacio", "冷凝"), ("fusion", "热熔"),
            ("electro", "导电"), ("aero", "气动"), ("spectro", "衍射"), ("havoc", "湮灭"),
        ]
        result = []
        for key, name in name_map:
            if key in self.resistance:
                v = self.resistance[key]
                val = int(v) if float(v).is_integer() else v
                result.append({"key": key, "name": name, "value": f"{val}%", "hi": v > 10})
        return result

    def get_intensity(self) -> List[Tuple[str, str]]:
        temp_cost = {0: "c1", 1: "c3", 2: "c4", 3: "c4"}
        temp_level = {0: "轻波级", 1: "巨浪级", 2: "怒涛级", 3: "海啸级"}
        result = []
        result.append(("声骸等级", temp_level[self.intensityCode]))
        result.append(("「COST」", temp_cost[self.intensityCode]))
        return result

    def get_group_name(self) -> List[str]:
        return [i["name"] for i in self.group.values()]