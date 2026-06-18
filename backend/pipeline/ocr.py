"""Leitura do HUD e do kill feed via PaddleOCR.

PaddleOCR é uma dependência pesada (extra `pipeline` em pyproject.toml) e só
é importada de fato dentro de `_engine()`, pra o resto da aplicação (API,
rotas, scraper) poder ser importado e testado sem precisar dela instalada.

As regiões de recorte (HUD, kill feed) variam por resolução de gravação —
ainda não calibradas contra vídeo real. Ajustar `HUD_REGION`/`KILLFEED_REGION`
assim que houver amostras reais de vídeo da Fase 0.
"""

from pathlib import Path
from typing import Any

HUD_REGION = (0, 0, 1, 1)  # (x0, y0, x1, y1) normalizado — TODO: calibrar
KILLFEED_REGION = (0, 0, 1, 1)  # TODO: calibrar

_engine_instance: Any = None


def _engine() -> Any:
    global _engine_instance
    if _engine_instance is None:
        from paddleocr import PaddleOCR  # import pesado, só quando usado de fato

        _engine_instance = PaddleOCR(lang="en")
    return _engine_instance


def _crop_normalized(image: Any, region: tuple[float, float, float, float]) -> Any:
    h, w = image.shape[:2]
    x0, y0, x1, y1 = region
    return image[int(y0 * h) : int(y1 * h), int(x0 * w) : int(x1 * w)]


def read_hud(frame_path: Path) -> dict[str, int | None]:
    """Lê CS/gold/level do HUD de um frame. Retorna None nos campos que não
    conseguir reconhecer, em vez de levantar exceção — um frame ilegível não
    deve derrubar o processamento da partida inteira."""
    import cv2

    image = cv2.imread(str(frame_path))
    crop = _crop_normalized(image, HUD_REGION)
    result = _engine().ocr(crop)
    text_fragments = [line[1][0] for block in result for line in block]
    return _parse_hud_fragments(text_fragments)


def read_killfeed(frame_path: Path) -> list[str]:
    import cv2

    image = cv2.imread(str(frame_path))
    crop = _crop_normalized(image, KILLFEED_REGION)
    result = _engine().ocr(crop)
    return [line[1][0] for block in result for line in block]


def _parse_hud_fragments(fragments: list[str]) -> dict[str, int | None]:
    """Tenta extrair CS/gold/level de strings OCR cruas. Implementação
    mínima — espera ajuste fino contra exemplos reais de HUD do Wild Rift."""
    parsed: dict[str, int | None] = {"cs": None, "gold": None, "level": None}
    for fragment in fragments:
        digits = "".join(c for c in fragment if c.isdigit())
        if not digits:
            continue
        value = int(digits)
        if parsed["cs"] is None and value < 1000:
            parsed["cs"] = value
        elif parsed["gold"] is None and value >= 1000:
            parsed["gold"] = value
    return parsed
