from __future__ import annotations
from typing import List, Optional

from pydantic import Field, BaseModel


class PermanentRouge(BaseModel):
    """浸梦海床"""

    maxScore: int  # 最大分数
    score: int  # 分数
    sort: int  # 排序
    title: str  # 标题


class PhantomBattleBadgeItem(BaseModel):
    """激斗！向着荣耀之丘"""

    iconUrl: str  # 图标
    name: str  # 名称
    sort: int  # 排序
    unlock: bool  # 是否解锁


class PhantomBattle(BaseModel):
    """激斗！向着荣耀之丘"""

    badgeList: List[PhantomBattleBadgeItem] = Field(default_factory=list)  # 勋章列表
    badgeNum: int  # 勋章数量
    cardNum: int  # 卡片数量
    exp: int  # 经验
    expLimit: int  # 经验上限
    level: int  # 等级
    levelIcon: str  # 等级图标
    levelName: str  # 等级名称
    maxBadgeNum: int  # 最大勋章数量
    maxCardNum: int  # 最大卡片数量
    sort: int  # 排序
    title: str  # 标题


class CountData(BaseModel):
    count: int
    total: int


class FloroRanch(BaseModel):
    """幻梦游园"""

    animalCount: CountData  # 动物数量
    mapCount: CountData  # 地图数量
    reward: CountData  # 奖励
    sort: int  # 排序
    title: str  # 标题
    toyCount: CountData  # 玩具数量


class HonamiStoryItem(BaseModel):
    icon: str  # 图标
    itemId: int  # 物品ID
    quality: int  # 品质
    title: str  # 标题
    unlock: bool  # 是否解锁


class HonamiStory(BaseModel):
    """穗波怪异物语"""

    itemNum: int  # 已解锁物品数量
    items: List[HonamiStoryItem] = Field(default_factory=list)  # 物品列表
    level: int  # 等级
    maxItemNum: int  # 最大物品数量
    sort: int  # 排序
    title: str  # 标题


class PhantomBattleRecord(BaseModel):
    """荣耀之丘：激斗重燃"""

    cardNum: int  # 卡片数量
    cardTotalNum: int  # 卡片总数
    exp: int  # 经验
    level: int  # 等级
    levelName: str  # 等级名称
    nextExp: int  # 下一级经验
    sort: int  # 排序
    title: str  # 标题


class TrapDefense(BaseModel):
    """潮蚀模拟"""

    high: CountData  # 高难度
    low: CountData  # 低难度
    sort: int  # 排序
    title: str  # 标题


class MoreActivity(BaseModel):
    """更多活动"""

    permanentRouge: Optional[PermanentRouge] = None  # 浸梦海床
    phantomBattle: Optional[PhantomBattle] = None  # 激斗！向着荣耀之丘
    floroRanch: Optional[FloroRanch] = None  # 幻梦游园
    honamiStory: Optional[HonamiStory] = None  # 穗波怪异物语
    phantomBattleRecord: Optional[PhantomBattleRecord] = None  # 荣耀之丘：激斗重燃
    trapDefense: Optional[TrapDefense] = None  # 潮蚀模拟
