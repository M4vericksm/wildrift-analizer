"""Heurísticas de eventos macro a partir do kill feed (texto) e da timeline.

Fase 0 não tem posição de campeões (isso é YOLO/minimapa, Fase 2 — ver
docs/decisions/0001-extracao-via-video.md), então as heurísticas aqui se
limitam ao que dá pra inferir de texto (kill feed) e dos números do HUD
(CS/gold ao longo do tempo). Nada de "gank ignorado" ou "fora de posição"
ainda — isso depende de saber onde os campeões estavam.
"""

import re
from dataclasses import dataclass

_KILL_RE = re.compile(r"(?P<killer>.+?)\s+(?:killed|matou)\s+(?P<victim>.+)", re.IGNORECASE)
_OBJECTIVE_RE = re.compile(
    r"(?P<objective>Dragon|Baron Nashor|Rift Herald|Dragão|Barão Nashor)\s+"
    r"(?:slain by|abatido por)\s+(?P<team>.+)",
    re.IGNORECASE,
)


@dataclass
class TimelinePoint:
    timestamp_seconds: int
    cs: int | None
    gold: int | None
    level: int | None


def parse_kill_feed_line(line: str) -> dict | None:
    """Converte uma linha de kill feed em um evento estruturado, ou None se
    a linha não corresponder a nenhum padrão conhecido."""
    objective_match = _OBJECTIVE_RE.match(line)
    if objective_match:
        return {
            "event_type": "objective",
            "data_json": {
                "objective": objective_match.group("objective"),
                "team": objective_match.group("team").strip(),
            },
        }
    kill_match = _KILL_RE.match(line)
    if kill_match:
        return {
            "event_type": "kill",
            "data_json": {
                "killer": kill_match.group("killer").strip(),
                "victim": kill_match.group("victim").strip(),
            },
        }
    return None


def build_events_from_kill_feed(
    lines: list[tuple[int, str]], player_name: str
) -> list[dict]:
    """`lines` é uma lista de (timestamp_seconds, texto_da_linha). Marca como
    'death' os kills em que a vítima é o próprio jogador."""
    events = []
    for timestamp_seconds, line in lines:
        parsed = parse_kill_feed_line(line)
        if parsed is None:
            continue
        if parsed["event_type"] == "kill" and parsed["data_json"]["victim"] == player_name:
            parsed = {"event_type": "death", "data_json": parsed["data_json"]}
        events.append({"timestamp_seconds": timestamp_seconds, **parsed})
    return events


def detect_repeated_killer(events: list[dict], min_count: int = 2) -> list[dict]:
    """Aponta quando o mesmo inimigo matou o jogador `min_count` vezes ou
    mais — padrão que vale citar no relatório mesmo sem dados de posição."""
    deaths_by_killer: dict[str, list[dict]] = {}
    for event in events:
        if event["event_type"] != "death":
            continue
        killer = event["data_json"]["killer"]
        deaths_by_killer.setdefault(killer, []).append(event)

    return [
        {
            "event_type": "repeated_death_pattern",
            "data_json": {
                "killer": killer,
                "count": len(deaths),
                "timestamps": [e["timestamp_seconds"] for e in deaths],
            },
        }
        for killer, deaths in deaths_by_killer.items()
        if len(deaths) >= min_count
    ]


def detect_cs_stall(
    timeline: list[TimelinePoint], threshold_seconds: int = 90
) -> list[dict]:
    """Aponta janelas onde o CS não cresceu por `threshold_seconds` ou mais,
    sinal aproximado de farm parado (pode ser morte, recall, ou teamfight —
    o LLM decide o que isso significa com o resto do contexto)."""
    points = [p for p in timeline if p.cs is not None]
    if len(points) < 2:
        return []

    stalls = []
    stall_start = points[0]
    for previous, current in zip(points, points[1:]):
        if current.cs > previous.cs:
            duration = previous.timestamp_seconds - stall_start.timestamp_seconds
            if duration >= threshold_seconds:
                stalls.append(
                    {
                        "event_type": "cs_stall",
                        "timestamp_seconds": stall_start.timestamp_seconds,
                        "data_json": {
                            "duration_seconds": duration,
                            "cs_at_stall": stall_start.cs,
                        },
                    }
                )
            stall_start = current

    return stalls
