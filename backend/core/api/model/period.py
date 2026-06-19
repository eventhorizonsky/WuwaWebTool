from __future__ import annotations
from typing import List, Optional, Union

from pydantic import Field, BaseModel


class Period(BaseModel):
    """资源简报"""

    title: str  # 标题
    index: int  # 索引


class PeriodList(BaseModel):
    """资源简报"""

    weeks: List[Period] = Field(default_factory=list)  # 周报列表
    months: List[Period] = Field(default_factory=list)  # 月报列表
    versions: List[Period] = Field(default_factory=list)  # 版本列表


class PeriodNode(BaseModel):
    type: str
    num: int


class PeriodDetailNode(BaseModel):
    type: str
    num: int
    sort: int


class PeriodDetailItem(BaseModel):
    type: int
    total: int
    inc: Optional[Union[int, str]] = None
    detail: List[PeriodDetailNode] = Field(default_factory=list)
    copyWriting: Optional[str] = None


class PeriodDetail(BaseModel):
    """资源简报详情"""

    totalCoin: Optional[int] = 0
    totalStar: Optional[int] = 0
    coinList: List[PeriodNode] = Field(default_factory=list)
    starList: List[PeriodNode] = Field(default_factory=list)
    itemList: List[PeriodDetailItem] = Field(default_factory=list)
    copyWriting: Optional[str] = None
