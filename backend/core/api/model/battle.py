from __future__ import annotations
from typing import Dict, List, Union, Optional

from pydantic import Field, BaseModel, model_validator


# 定义角色模型
class AbyssRole(BaseModel):
    roleId: int
    iconUrl: Optional[str] = None


# 定义楼层模型
class AbyssFloor(BaseModel):
    floor: int
    picUrl: str
    star: int
    roleList: Optional[List[AbyssRole]] = None


# 定义区域模型
class AbyssArea(BaseModel):
    areaId: int
    areaName: str
    star: int
    maxStar: int
    floorList: Optional[List[AbyssFloor]] = None


# 定义难度模型
class AbyssDifficulty(BaseModel):
    difficulty: int
    difficultyName: str
    towerAreaList: List[AbyssArea]


# 定义顶层模型
class AbyssChallenge(BaseModel):
    isUnlock: bool
    seasonEndTime: Optional[int]
    difficultyList: Optional[List[AbyssDifficulty]]


class ChallengeRole(BaseModel):
    roleName: str
    roleHeadIcon: str
    roleLevel: int


class Challenge(BaseModel):
    challengeId: int
    bossHeadIcon: str
    bossIconUrl: str
    bossLevel: int
    bossName: str
    passTime: int
    difficulty: int
    roles: Optional[List[ChallengeRole]] = None


class ChallengeArea(BaseModel):
    challengeInfo: Dict[str, List[Challenge]]
    open: bool = False
    isUnlock: bool = False

    @model_validator(mode="before")
    @classmethod
    def validate_depending_on_unlock(cls, data):
        """根据 isUnlock 状态预处理数据"""
        if isinstance(data, dict):
            if not data.get("isUnlock", False):
                # 创建一个新的数据字典，只保留基本字段
                new_data = {"isUnlock": False, "open": data.get("open", False)}

                # 将 areaId 和 areaName 设置为 None
                new_data["areaId"] = None
                new_data["areaName"] = None

                # 创建一个空的 challengeInfo 字典
                new_data["challengeInfo"] = {}

                return new_data

        return data


class ExploreItem(BaseModel):
    name: str
    progress: int
    type: int
    icon: Optional[str] = None


class AreaInfo(BaseModel):
    areaId: int
    areaName: str
    areaProgress: int
    itemList: List[ExploreItem]


class ExploreCountry(BaseModel):
    countryId: int
    countryName: str
    detailPageFontColor: str
    detailPagePic: str
    detailPageProgressColor: str
    homePageIcon: str


class ExploreArea(BaseModel):
    areaInfoList: Union[List[AreaInfo], None] = None
    country: ExploreCountry
    countryProgress: str


class ExploreList(BaseModel):
    """探索度"""

    exploreList: Union[List[ExploreArea], None] = None
    open: bool


class SlashRole(BaseModel):
    iconUrl: str  # 角色头像
    roleId: int  # 角色ID


class SlashHalf(BaseModel):
    buffDescription: str  # 描述
    buffIcon: str  # 图标
    buffName: str  # 名称
    buffQuality: int  # 品质
    roleList: List[SlashRole]  # 角色列表
    score: int  # 分数


class SlashChallenge(BaseModel):
    challengeId: int  # 挑战ID
    challengeName: str  # 挑战名称
    halfList: List[Optional[SlashHalf]] = Field(default_factory=list)  # 半场列表
    rank: Optional[str] = Field(default="")  # 等级
    score: int  # 分数

    @model_validator(mode="before")
    @classmethod
    def filter_null_halves(cls, data):
        if isinstance(data, dict) and "halfList" in data:
            data["halfList"] = [h for h in data["halfList"] if h is not None]
        return data

    def get_rank(self):
        if not self.rank:
            return ""
        return self.rank.lower()


class SlashDifficulty(BaseModel):
    allScore: int  # 总分数
    challengeList: List[SlashChallenge] = Field(default_factory=list)  # 挑战列表
    difficulty: int  # 难度
    difficultyName: str  # 难度名称
    homePageBG: str  # 首页背景
    maxScore: int  # 最大分数
    teamIcon: str  # 团队图标


class SlashDetail(BaseModel):
    """冥海"""

    isUnlock: bool  # 是否解锁
    seasonEndTime: int  # 赛季结束时间
    difficultyList: List[SlashDifficulty] = Field(default_factory=list)  # 难度列表


# ============================================================
# 终焉矩阵 (Matrix / newTower)
# ============================================================


class MatrixBuff(BaseModel):
    """矩阵buff"""

    buffIcon: str = ""  # buff图标
    buffId: int = 0  # buffID
    buffName: str = ""  # buff名称
    desc: str = ""  # buff描述


class MatrixTeam(BaseModel):
    """矩阵队伍"""

    bossCount: int = 0  # 该队伍面对的boss数
    buffs: List[MatrixBuff] = Field(default_factory=list)  # buff列表
    passBoss: int = 0  # 击败的boss数
    roleIcons: List[str] = Field(default_factory=list)  # 角色头像URL列表
    round: int = 0  # 轮次
    score: int = 0  # 队伍得分


class MatrixMode(BaseModel):
    """矩阵模式 (modeId=1: 奇点扩张, modeId=0: 稳态协议)"""

    hasRecord: bool = False  # 是否有记录
    isUnlock: bool = False  # 是否解锁
    modeId: int = 0  # 模式ID
    rank: int = 0  # 排名
    score: int = 0  # 总分数
    # 以下字段仅在 Detail 接口中返回
    bossCount: Optional[int] = None  # boss总数
    passBoss: Optional[int] = None  # 击败boss数
    round: Optional[int] = None  # 轮次
    teams: List[MatrixTeam] = Field(default_factory=list)  # 队伍列表


class MatrixDetail(BaseModel):
    """终焉矩阵"""

    isUnlock: bool  # 是否解锁
    endTime: int = 0  # 赛季结束时间
    modeDetails: List[MatrixMode] = Field(default_factory=list)  # 模式列表
    reward: int = 0  # 已领取奖励
    totalReward: int = 0  # 总奖励
