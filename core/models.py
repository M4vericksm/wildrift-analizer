import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class MatchStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    error = "error"


class MatchResult(str, enum.Enum):
    win = "win"
    loss = "loss"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    matches: Mapped[list["Match"]] = relationship(back_populates="user")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    video_url: Mapped[str] = mapped_column(String)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus), default=MatchStatus.pending, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    champion_played: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    result: Mapped[MatchResult | None] = mapped_column(Enum(MatchResult), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="matches")
    timelines: Mapped[list["Timeline"]] = relationship(back_populates="match")
    events: Mapped[list["Event"]] = relationship(back_populates="match")
    analysis: Mapped["Analysis | None"] = relationship(back_populates="match", uselist=False)


class Timeline(Base):
    __tablename__ = "timelines"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), index=True)
    timestamp_seconds: Mapped[int] = mapped_column(Integer)
    cs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    position_y: Mapped[float | None] = mapped_column(Float, nullable=True)

    match: Mapped[Match] = relationship(back_populates="timelines")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), index=True)
    timestamp_seconds: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String)  # 'death' | 'kill' | 'objective' | 'gank_ignored'
    data_json: Mapped[dict] = mapped_column(JSON, default=dict)

    match: Mapped[Match] = relationship(back_populates="events")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), unique=True, index=True)
    summary_markdown: Mapped[str] = mapped_column(Text)
    top_mistakes_json: Mapped[list] = mapped_column(JSON, default=list)
    top_good_plays_json: Mapped[list] = mapped_column(JSON, default=list)
    llm_model_used: Mapped[str] = mapped_column(String)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    match: Mapped[Match] = relationship(back_populates="analysis")


class MetaChampion(Base):
    __tablename__ = "meta_champions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    champion_name: Mapped[str] = mapped_column(String, index=True)
    patch: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)
    tier: Mapped[str | None] = mapped_column(String, nullable=True)
    winrate: Mapped[float | None] = mapped_column(Float, nullable=True)
    pickrate: Mapped[float | None] = mapped_column(Float, nullable=True)
    banrate: Mapped[float | None] = mapped_column(Float, nullable=True)
    build_items_json: Mapped[list] = mapped_column(JSON, default=list)
    runes_json: Mapped[dict] = mapped_column(JSON, default=dict)
    skill_order_json: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String)  # 'wildlegends' | 'lolm_qq'


class MetaPatch(Base):
    __tablename__ = "meta_patches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    patch_version: Mapped[str] = mapped_column(String, unique=True, index=True)
    release_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
