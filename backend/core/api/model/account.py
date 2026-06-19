from __future__ import annotations
from typing import List, Union, Optional

from msgspec import UNSET, Struct, UnsetType, field
from pydantic import BaseModel


class GeneralGeetestData(Struct):
    geetest_challenge: str
    geetest_seccode: str
    geetest_validate: str


class GeneralV1SendPhoneCodeRequest(Struct):
    phone: str
    type: int
    captcha: Union[GeneralGeetestData, UnsetType] = field(default=UNSET)


class Box(BaseModel):
    boxName: str
    num: int


class Box2(BaseModel):
    name: str
    num: int


class AccountBaseInfo(BaseModel):
    """账户基本信息"""

    name: str  # 名字
    id: int  # 特征码
    creatTime: Optional[int] = None  # 创建时间 秒级 unix 时间戳
    activeDays: Optional[int] = None  # 活跃天数
    level: Optional[int] = None  # 等级
    worldLevel: Optional[int] = None  # 世界等级
    roleNum: Optional[int] = None  # 角色数量
    bigCount: Optional[int] = None  # 大型信标解锁数
    smallCount: Optional[int] = None  # 小型信标解锁数
    achievementCount: Optional[int] = None  # 成就数量
    achievementStar: Optional[int] = None  # 成就星数
    boxList: Optional[List[Optional[Box]]] = None  # 宝箱
    treasureBoxList: Optional[List[Optional[Box2]]] = None  # 宝箱
    weeklyInstCount: Optional[int] = None  # 周本次数
    weeklyInstCountLimit: Optional[int] = None  # 周本限制次数
    storeEnergy: Optional[int] = None  # 结晶单质数量
    storeEnergyLimit: Optional[int] = None  # 结晶单质限制
    rougeScore: Optional[int] = None  # 千道门扉的异想
    rougeScoreLimit: Optional[int] = None  # 千道门扉的异想限制

    @property
    def is_full(self):
        """完整数据，没有隐藏库街区数据"""
        return isinstance(self.creatTime, int)


class KuroRoleInfo(BaseModel):
    """库洛角色信息"""

    id: int
    userId: int
    gameId: int
    serverId: str
    serverName: str
    roleId: str
    roleName: str
    gameHeadUrl: str
    roleNum: int
    achievementCount: int


class KuroWavesUserInfo(BaseModel):
    """库洛用户信息"""

    id: int
    userId: int
    gameId: int
    serverId: str
    roleId: str
    roleName: str
