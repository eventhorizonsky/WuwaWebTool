from __future__ import annotations
from pydantic import Field, BaseModel


class EnemyDetailData(BaseModel):
    enemy_resistance: int = Field(default=10)  # 怪物抗性
    enemy_level: int = Field(default=90)  # 怪物等级
