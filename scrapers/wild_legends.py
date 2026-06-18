"""Scraper do Wild Legends (wildlegends.net) — fonte primária de meta
(docs/architecture.md, bloco 7).

IMPORTANTE — seletores não calibrados: este ambiente de desenvolvimento não
teve acesso de rede a wildlegends.net (host fora da allowlist de egress da
sandbox) no momento em que este scraper foi escrito. `_CHAMPION_CARD_SELECTOR`
e os seletores em `parse_champion_guide` são heurísticas razoáveis para um
site de guias (cards de campeão com link + dados de build/runas/tier numa
página por campeão), não confirmadas contra o HTML real. Antes de rodar em
produção: abrir https://wildlegends.net/guias e a página de um campeão no
navegador, inspecionar os seletores reais e ajustar as duas funções de parse
abaixo. Os testes em tests/test_wild_legends_scraper.py validam a lógica de
parsing contra um fixture ilustrativo, não contra o markup real do site.
"""

from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from core.db import SessionLocal
from scrapers.common import make_client, upsert_meta_champion

BASE_URL = "https://wildlegends.net"
GUIDES_PATH = "/guias"
SOURCE = "wildlegends"

_CHAMPION_CARD_SELECTOR = "a.champion-card"  # TODO: confirmar contra o site real


def parse_champion_list(html: str) -> list[dict]:
    """Extrai [{'name': ..., 'guide_url': ...}] da página de listagem de guias."""
    soup = BeautifulSoup(html, "html.parser")
    champions = []
    for card in soup.select(_CHAMPION_CARD_SELECTOR):
        name = card.get("data-champion-name") or card.get_text(strip=True)
        href = card.get("href")
        if not name or not href:
            continue
        champions.append({"name": name.strip(), "guide_url": urljoin(BASE_URL, href)})
    return champions


def parse_champion_guide(html: str, champion_name: str) -> dict:
    """Extrai patch/role/tier/winrate/build/runas/skill_order da página de
    guia de um campeão específico."""
    soup = BeautifulSoup(html, "html.parser")

    def text_or_none(selector: str) -> str | None:
        node = soup.select_one(selector)
        return node.get_text(strip=True) if node else None

    return {
        "champion_name": champion_name,
        "patch": text_or_none(".patch-version") or "unknown",
        "role": text_or_none(".champion-role") or "",
        "tier": text_or_none(".champion-tier"),
        "winrate": _parse_percent(text_or_none(".stat-winrate")),
        "pickrate": _parse_percent(text_or_none(".stat-pickrate")),
        "banrate": _parse_percent(text_or_none(".stat-banrate")),
        "build_items": [item.get_text(strip=True) for item in soup.select(".build-items .item")],
        "runes": {
            rune.get("data-rune-slot", str(i)): rune.get_text(strip=True)
            for i, rune in enumerate(soup.select(".runes .rune"))
        },
        "skill_order": [skill.get_text(strip=True) for skill in soup.select(".skill-order .skill")],
    }


def _parse_percent(value: str | None) -> float | None:
    if not value:
        return None
    digits = value.replace("%", "").replace(",", ".").strip()
    try:
        return float(digits)
    except ValueError:
        return None


def run_once(db: Session | None = None) -> int:
    """Raspa a listagem + cada guia de campeão e grava em meta_champions.
    Retorna a quantidade de campeões atualizados."""
    owns_session = db is None
    db = db or SessionLocal()
    updated = 0
    try:
        with make_client() as client:
            listing_response = client.get(urljoin(BASE_URL, GUIDES_PATH))
            listing_response.raise_for_status()
            champions = parse_champion_list(listing_response.text)

            for champion in champions:
                try:
                    guide_response = client.get(champion["guide_url"])
                    guide_response.raise_for_status()
                    parsed = parse_champion_guide(guide_response.text, champion["name"])
                    upsert_meta_champion(db, parsed, source=SOURCE)
                    updated += 1
                except httpx.HTTPError:
                    continue
    finally:
        if owns_session:
            db.close()
    return updated


if __name__ == "__main__":
    count = run_once()
    print(f"{count} campeões atualizados a partir de {SOURCE}.")
