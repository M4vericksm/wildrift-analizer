"""Orquestra o processamento de uma partida (Fase 0: roda em BackgroundTasks,
sem fila — ver docs/decisions/0002-fase-0-sem-fila-sem-gpu.md).

Mantido enxuto de propósito: cada etapa pesada (ffmpeg, OCR, LLM) vive no
próprio módulo dela; este arquivo só costura a sequência e persiste o
resultado.
"""

import tempfile
from pathlib import Path

from sqlalchemy.orm import Session

from backend.pipeline.extract import extract_frames
from backend.pipeline.heuristics import (
    TimelinePoint,
    build_events_from_kill_feed,
    detect_cs_stall,
    detect_repeated_killer,
)
from backend.pipeline.ocr import read_hud, read_killfeed
from backend.services.llm import get_llm_client
from backend.services.storage import Storage
from core.models import Analysis, Event, Match, MatchStatus, MetaChampion, Timeline


def process_match(match_id: str, db: Session, storage: Storage) -> None:
    match = db.get(Match, match_id)
    if match is None:
        return

    match.status = MatchStatus.processing
    db.commit()

    try:
        _run_pipeline(match, db, storage)
        match.status = MatchStatus.ready
    except Exception as exc:  # noqa: BLE001 — qualquer falha marca a partida como erro
        match.status = MatchStatus.error
        match.error_message = str(exc)
    finally:
        db.commit()


def _run_pipeline(match: Match, db: Session, storage: Storage) -> None:
    video_path = storage.path_for(match.video_url)

    with tempfile.TemporaryDirectory() as tmp:
        frames_dir = Path(tmp)
        frames = extract_frames(video_path, frames_dir, fps=1)

        timeline_points: list[TimelinePoint] = []
        kill_feed_lines: list[tuple[int, str]] = []
        for second, frame in enumerate(frames):
            hud = read_hud(frame)
            timeline_points.append(TimelinePoint(timestamp_seconds=second, **hud))
            for line in read_killfeed(frame):
                kill_feed_lines.append((second, line))

        for point in timeline_points:
            db.add(
                Timeline(
                    match_id=match.id,
                    timestamp_seconds=point.timestamp_seconds,
                    cs=point.cs,
                    gold=point.gold,
                    level=point.level,
                )
            )

        player_name = match.champion_played or ""
        events = build_events_from_kill_feed(kill_feed_lines, player_name)
        events += detect_repeated_killer(events)
        events += detect_cs_stall(timeline_points)

        for event in events:
            db.add(
                Event(
                    match_id=match.id,
                    timestamp_seconds=event["timestamp_seconds"],
                    event_type=event["event_type"],
                    data_json=event["data_json"],
                )
            )

    meta = (
        db.query(MetaChampion)
        .filter(MetaChampion.champion_name == match.champion_played)
        .order_by(MetaChampion.updated_at.desc())
        .first()
    )

    llm = get_llm_client()
    report_markdown = llm.generate_report(
        {
            "meta": _format_meta(meta),
            "match_summary": _format_match_summary(match),
            "events": _format_events(events),
        }
    )

    db.add(
        Analysis(
            match_id=match.id,
            summary_markdown=report_markdown,
            top_mistakes_json=[e for e in events if e["event_type"] in ("death", "repeated_death_pattern")],
            top_good_plays_json=[],
            llm_model_used=llm.model_name,
        )
    )

    storage.delete(match.video_url)  # retenção — ADR 0003


def _format_meta(meta: MetaChampion | None) -> str:
    if meta is None:
        return "Sem dados de meta para este campeão no patch atual."
    return (
        f"Campeão: {meta.champion_name} ({meta.role}). Patch {meta.patch}. "
        f"Tier {meta.tier}. Winrate {meta.winrate}%. "
        f"Build sugerida: {meta.build_items_json}. Runas: {meta.runes_json}."
    )


def _format_match_summary(match: Match) -> str:
    result = match.result.value if match.result else "desconhecido"
    return f"Campeão: {match.champion_played} ({match.role}). Resultado: {result}."


def _format_events(events: list[dict]) -> str:
    return "\n".join(
        f"- {e['timestamp_seconds']}s: {e['event_type']} — {e['data_json']}"
        for e in events
    )
