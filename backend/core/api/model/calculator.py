from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel, RootModel


class OnlineWeapon(BaseModel):
    """
    {
        "weaponId": 21010011,
        "weaponName": "教学长刃",
        "weaponType": 1,
        "weaponStarLevel": 1,
        "weaponIcon": "https://web-static.kurobbs.com/adminConfig/29/weapon_icon/1716031228478.png",
        "isPreview": false,
        "isNew": false,
        "priority": 1,
        "acronym": "jxcr"
    }
    """

    weaponId: int
    weaponName: str
    weaponType: int
    weaponStarLevel: int
    weaponIcon: str
    isPreview: bool
    isNew: bool
    priority: int
    acronym: str


class OnlineWeaponList(RootModel[List[OnlineWeapon]]):
    def __iter__(self):
        return iter(self.root)


class OnlineRole(BaseModel):
    """
    {
        "roleId": 1102,
        "roleName": "散华",
        "roleIconUrl": "https://web-static.kurobbs.com/adminConfig/98/role_icon/1738924370710.png",
        "starLevel": 4,
        "attributeId": 1,
        "attributeName": null,
        "weaponTypeId": 2,
        "weaponTypeName": "迅刀",
        "acronym": "sh",
        "isPreview": false,
        "isNew": false,
        "priority": 4
    }
    """

    roleId: int
    roleName: str
    roleIconUrl: str
    starLevel: int
    attributeId: int
    # attributeName: Optional[str]
    weaponTypeId: int
    weaponTypeName: str
    acronym: str
    isPreview: bool
    isNew: bool
    priority: int


class OnlineRoleList(RootModel[List[OnlineRole]]):
    def __iter__(self):
        return iter(self.root)


class OnlinePhantom(BaseModel):
    """
    {
        "phantomId": 390080005,
        "name": "鸣钟之龟",
        "cost": 4,
        "risk": "海啸级",
        "iconUrl": "https://web-static.kurobbs.com/adminConfig/35/phantom_icon/1716031298428.png",
        "isPreview": false,
        "isNew": false,
        "priority": 104,
        "fetterIds": "8,7",
        "acronym": "mzzg"
    }
    """

    phantomId: int
    name: str
    cost: int
    risk: str
    iconUrl: str
    isPreview: bool
    isNew: bool
    priority: int
    fetterIds: str
    acronym: str


class OnlinePhantomList(RootModel[List[OnlinePhantom]]):
    def __iter__(self):
        return iter(self.root)


class OwnedRoleInfo(BaseModel):
    """已拥有角色信息
    {
        "roleId": 1402,
        "level": 90
    }
    """

    roleId: int
    level: int


class OwnedRoleInfoResponse(BaseModel):
    """已拥有角色信息响应"""

    roleInfoList: List[OwnedRoleInfo]


class EquipWeapon(BaseModel):
    """装备的武器
    {
        "id": 21010056,
        "breach": 6,
        "level": 90
    }
    """

    id: int
    breach: int
    level: int


class RoleCultivateSkillLevel(BaseModel):
    type: str
    level: int


class RoleCultivateStatus(BaseModel): # 这里暂时没有谐度破坏
    """角色培养状态
    {
        "roleId": 1107,
        "roleName": "珂莱塔",
        "roleLevel": 90,
        "roleBreakLevel": 6,
        "equipWeapon": {
            "id": 21010056,
            "breach": 6,
            "level": 90
        },
        "skillLevelList": [{
                "type": "常态攻击",
                "level": 1
        }, {
                "type": "共鸣技能",
                "level": 10
        }, {
                "type": "共鸣解放",
                "level": 10
        }, {
                "type": "变奏技能",
                "level": 6
        }, {
                "type": "共鸣回路",
                "level": 10
        }, {
                "type": "延奏技能",
                "level": 1
        }],
        "skillBreakList": ["2-3", "3-3", "2-1", "2-2", "2-4", "2-5", "3-1", "3-2", "3-4", "3-5"]
    }
    """

    roleId: int
    roleName: str
    roleLevel: int
    roleBreakLevel: int  # 突破等级
    equipWeapon: Optional[EquipWeapon] = None  # 装备的武器
    skillLevelList: List[RoleCultivateSkillLevel]
    skillBreakList: List[str]  # 突破技能


class RoleCultivateStatusList(RootModel[List[RoleCultivateStatus]]):
    def __iter__(self):
        return iter(self.root)


class CultivateCost(BaseModel):
    """培养成本
    {
        "id": "2",
        "name": "贝币",
        "iconUrl": "https://web-static.kurobbs.com/gamerdata/calculator/coin.png",
        "num": 4460260,
        "type": 0,
        "quality": 3,
        "isPreview": false
    }
    """

    id: str
    name: str
    iconUrl: str
    num: int
    type: int
    quality: int
    isPreview: bool


class Strategy(BaseModel):
    """攻略"""

    postId: str
    postTitle: str


class RoleCostDetail(BaseModel):
    """角色培养详情"""

    allCost: Optional[List[CultivateCost]] = None
    missingCost: Optional[List[CultivateCost]] = None
    synthetic: Optional[List[CultivateCost]] = None
    missingRoleCost: Optional[List[CultivateCost]] = None
    missingSkillCost: Optional[List[CultivateCost]] = None
    missingWeaponCost: Optional[List[CultivateCost]] = None
    roleId: int
    weaponId: Optional[int] = None
    strategyList: Optional[List[Strategy]] = None
    showStrategy: Optional[bool] = None


class BatchRoleCostResponse(BaseModel):
    """角色培养成本"""

    roleNum: int  # 角色数量
    weaponNum: int  # 武器数量
    # preview: Dict[str, Optional[List[CultivateCost]]]
    costList: List[RoleCostDetail]  # 每个角色的详细花费
