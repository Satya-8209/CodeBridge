from pydantic import BaseModel
from typing import Optional


class AlertIn(BaseModel):
    title: str
    service: str
    severity: str = "high"   # critical | high | medium | low
    error_log: str


class ResolveIn(BaseModel):
    alert_id: str
    title: str
    service: str
    root_cause: str
    fix_applied: str
    time_to_resolve_minutes: int = 0


class MemoryMatch(BaseModel):
    text: str
    score: Optional[float] = None


class AgentResponse(BaseModel):
    alert_id: str
    similar_incidents: list[MemoryMatch]
    suggestion: str
    memory_hit: bool   # True if memory found relevant past incidents
