from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel


class DataReviewPage1(BaseModel):
    """登录签到数据"""

    loginDay: Optional[int] = None
    maxContinueSignDay: Optional[int] = None
    registerTime: Optional[str] = None
    signScorePercent: Optional[int] = None


class DataReviewPage2(BaseModel):
    """活跃时间"""

    latestEnterTime: Optional[str] = None
    oftenUseTimeType: Optional[str] = None
    postTitle: Optional[str] = None
    toolName: Optional[str] = None


class DataReviewPage3(BaseModel):
    """工具使用"""

    akiMonthSignCount: Optional[int] = None
    haruMonthSignCount: Optional[int] = None
    topEnterAkiNames: Optional[List[str]] = None
    topEnterHaruNames: Optional[List[str]] = None
    topEnterToolCount: Optional[int] = None
    topEnterToolName: Optional[str] = None


class DataReviewPage4(BaseModel):
    """浏览数据"""

    readForumNames: Optional[List[str]] = None
    readPostTotalCount: Optional[int] = None
    singleTopReadCount: Optional[int] = None
    singleTopReadDate: Optional[str] = None
    topForumCount: Optional[int] = None
    topForumName: Optional[str] = None


class DataReviewPage5(BaseModel):
    """库洛币"""

    coinScorePercent: Optional[int] = None
    incomeCoin: Optional[int] = None


class DataReviewPage6(BaseModel):
    """互动数据"""

    playCount: Optional[int] = None
    playUser: Optional[str] = None
    toPlayCount: Optional[int] = None
    toPlayUser: Optional[str] = None


class DataReviewPage7(BaseModel):
    """社交数据"""

    fanCount: Optional[int] = None
    followCount: Optional[int] = None
    publishPostCount: Optional[int] = None
    topTopicNames: Optional[List[str]] = None


class DataReviewPage8(BaseModel):
    """互动统计"""

    popularCommentLikeCount: Optional[int] = None
    popularPostLikeCount: Optional[int] = None
    totalCollectCount: Optional[int] = None
    totalCommentCount: Optional[int] = None
    totalLikeCount: Optional[int] = None


class SummaryOther(BaseModel):
    nums: Optional[int] = None
    power: Optional[int] = None
    score: Optional[float] = None
    type: Optional[int] = None


class DataReviewSummary(BaseModel):
    """总结"""

    other: Optional[List[SummaryOther]] = None
    titles: Optional[List[str]] = None
    yearKeyword: Optional[str] = None


class DataReview(BaseModel):
    """年度数据回顾"""

    hasFinish: Optional[bool] = None
    hasShare: Optional[bool] = None
    isYellow: Optional[bool] = None
    page1: Optional[DataReviewPage1] = None
    page2: Optional[DataReviewPage2] = None
    page3: Optional[DataReviewPage3] = None
    page4: Optional[DataReviewPage4] = None
    page5: Optional[DataReviewPage5] = None
    page6: Optional[DataReviewPage6] = None
    page7: Optional[DataReviewPage7] = None
    page8: Optional[DataReviewPage8] = None
    showType: Optional[int] = None
    summary: Optional[DataReviewSummary] = None
    userId: Optional[str] = None
    userName: Optional[str] = None
