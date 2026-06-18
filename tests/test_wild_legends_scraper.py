"""Testa a lógica de parsing do scraper contra um fixture ilustrativo — não
contra o HTML real do site (ver aviso no topo de scrapers/wild_legends.py
sobre por que os seletores ainda não foram calibrados)."""

from scrapers.wild_legends import parse_champion_guide, parse_champion_list

LISTING_HTML = """
<html><body>
  <a class="champion-card" href="/guia/yasuo" data-champion-name="Yasuo"></a>
  <a class="champion-card" href="/guia/lux" data-champion-name="Lux"></a>
</body></html>
"""

GUIDE_HTML = """
<html><body>
  <span class="patch-version">7.1B</span>
  <span class="champion-role">Mid</span>
  <span class="champion-tier">B</span>
  <span class="stat-winrate">49.2%</span>
  <span class="stat-pickrate">8.1%</span>
  <span class="stat-banrate">2.4%</span>
  <div class="build-items"><span class="item">Lâmina Infinita</span><span class="item">Borla da Morte</span></div>
  <div class="runes"><span class="rune" data-rune-slot="keystone">Conquistador</span></div>
  <div class="skill-order"><span class="skill">Q</span><span class="skill">E</span></div>
</body></html>
"""


def test_parse_champion_list():
    champions = parse_champion_list(LISTING_HTML)

    assert champions == [
        {"name": "Yasuo", "guide_url": "https://wildlegends.net/guia/yasuo"},
        {"name": "Lux", "guide_url": "https://wildlegends.net/guia/lux"},
    ]


def test_parse_champion_guide():
    parsed = parse_champion_guide(GUIDE_HTML, "Yasuo")

    assert parsed["champion_name"] == "Yasuo"
    assert parsed["patch"] == "7.1B"
    assert parsed["role"] == "Mid"
    assert parsed["tier"] == "B"
    assert parsed["winrate"] == 49.2
    assert parsed["build_items"] == ["Lâmina Infinita", "Borla da Morte"]
    assert parsed["runes"] == {"keystone": "Conquistador"}
    assert parsed["skill_order"] == ["Q", "E"]
