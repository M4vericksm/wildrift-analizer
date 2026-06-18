from datetime import datetime

from pydantic import BaseModel

from core.models import MatchResult, MatchStatus


class MatchOut(BaseModel):
    id: str
    status: MatchStatus
    champion_played: str | None
    role: str | None
    result: MatchResult | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    summary_markdown: str
    top_mistakes_json: list
    top_good_plays_json: list
    llm_model_used: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class MatchDetailOut(MatchOut):
    analysis: AnalysisOut | None = None


class MatchStatusOut(BaseModel):
    status: MatchStatus
    error_message: str | None = None


class MetaChampionOut(BaseModel):
    champion_name: str
    patch: str
    role: str
    tier: str | None
    winrate: float | None
    pickrate: float | None
    banrate: float | None
    build_items_json: list
    runes_json: dict
    skill_order_json: list
    source: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class MetaPatchOut(BaseModel):
    patch_version: str
    release_date: datetime | None
    notes: str | None

    model_config = {"from_attributes": True}
