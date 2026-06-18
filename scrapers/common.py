"""Utilidades compartilhadas pelos scrapers de meta.

Ver docs/decisions/0004-scraper-lolm-qq-risco.md: o Wild Legends é a fonte
crítica, qualquer outra fonte é best-effort e não pode derrubar esta.
"""

from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from core.models import MetaChampion

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def make_client(timeout: float = 15.0) -> httpx.Client:
    return httpx.Client(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True)


def upsert_meta_champion(db: Session, parsed: dict, source: str) -> MetaChampion:
    """Atualiza o registro existente (mesmo campeão+patch+source) ou cria um
    novo. Mantém histórico entre patches em vez de sobrescrever."""
    existing = (
        db.query(MetaChampion)
        .filter(
            MetaChampion.champion_name == parsed["champion_name"],
            MetaChampion.patch == parsed["patch"],
            MetaChampion.source == source,
        )
        .first()
    )
    record = existing or MetaChampion(
        champion_name=parsed["champion_name"], patch=parsed["patch"], source=source
    )
    record.role = parsed.get("role", record.role if existing else "")
    record.tier = parsed.get("tier")
    record.winrate = parsed.get("winrate")
    record.pickrate = parsed.get("pickrate")
    record.banrate = parsed.get("banrate")
    record.build_items_json = parsed.get("build_items", [])
    record.runes_json = parsed.get("runes", {})
    record.skill_order_json = parsed.get("skill_order", [])
    record.updated_at = datetime.utcnow()

    if not existing:
        db.add(record)
    db.commit()
    return record
