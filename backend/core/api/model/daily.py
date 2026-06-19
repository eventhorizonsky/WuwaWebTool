from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel


class EnergyData(BaseModel):
    """结晶波片"""

    name: str
    img: str
    refreshTimeStamp: int
    cur: int
    total: int


class LivenessData(BaseModel):
    """活跃度"""

    name: str
    img: str
    cur: int
    total: int


class BattlePassData(BaseModel):
    """电台"""

    name: str
    cur: int
    total: int


class TowerData(BaseModel):
    """逆境深塔"""

    name: str
    img: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    status: Optional[int] = None
    cur: int
    total: int
    refreshTimeStamp: int
    timePreDesc: Optional[str] = None
    expireTimeStamp: Optional[int] = None


class SlashTowerData(BaseModel):
    """冥歌海墟"""

    name: str
    img: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    status: Optional[int] = None
    cur: int
    total: int
    refreshTimeStamp: int
    timePreDesc: Optional[str] = None
    expireTimeStamp: Optional[int] = None


class WeeklyData(BaseModel):
    """周本"""

    name: str
    img: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    status: Optional[int] = None
    cur: int
    total: int
    refreshTimeStamp: int
    timePreDesc: Optional[str] = None
    expireTimeStamp: Optional[int] = None


class WeeklyRougeData(BaseModel):
    """千道门扉的异想"""

    name: Optional[str] = None
    img: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    status: Optional[int] = None
    cur: Optional[int] = None
    total: Optional[int] = None
    refreshTimeStamp: Optional[int] = None
    timePreDesc: Optional[str] = None
    expireTimeStamp: Optional[int] = None


class WeeklyFrameData(BaseModel):
    """周度游历"""

    name: str
    img: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    status: Optional[int] = None
    cur: int
    total: int
    refreshTimeStamp: int
    timePreDesc: Optional[str] = None
    expireTimeStamp: Optional[int] = None


class StoreEnergyData(BaseModel):
    """结晶单质"""

    name: str
    img: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    status: Optional[int] = None
    cur: int
    total: int
    refreshTimeStamp: int
    timePreDesc: Optional[str] = None
    expireTimeStamp: Optional[int] = None


class DailyData(BaseModel):
    """每日数据"""

    gameId: int
    userId: int
    serverId: str
    roleId: str
    roleName: str
    signInTxt: str
    hasSignIn: bool
    energyData: EnergyData
    livenessData: LivenessData
    battlePassData: List[BattlePassData]
    storeEnergyData: Optional[StoreEnergyData] = None
    towerData: Optional[TowerData] = None
    slashTowerData: Optional[SlashTowerData] = None
    weeklyData: Optional[WeeklyData] = None
    weeklyRougeData: Optional[WeeklyRougeData] = None
    weeklyFrameData: Optional[WeeklyFrameData] = None
