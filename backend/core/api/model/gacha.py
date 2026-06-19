from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class GachaLog(BaseModel):
    """抽卡记录"""

    model_config = ConfigDict(extra="allow")

    cardPoolType: str
    resourceId: int
    qualityLevel: int
    resourceType: str
    name: str
    count: int
    time: str

    def __hash__(self):
        return hash((self.resourceId, self.time))

    def match_key(self):
        """用于匹配的key，忽略resourceType字段（不同数据源可能标记不同）"""
        return (self.cardPoolType, self.resourceId, self.qualityLevel,
                self.name, self.count, self.time)
