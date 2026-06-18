"""Storage de vídeo da partida.

Fase 0: disco local (ver docs/decisions/0002-fase-0-sem-fila-sem-gpu.md).
Fase 1+: troca para Cloudflare R2 (docs/decisions/0003-storage-r2-retencao.md)
implementando a mesma interface — nenhum outro módulo deve saber onde o
vídeo está fisicamente guardado, só falar com esta interface.
"""

import shutil
import uuid
from pathlib import Path
from typing import BinaryIO, Protocol

from core.config import settings


class Storage(Protocol):
    def save(self, fileobj: BinaryIO, filename: str) -> str:
        """Salva o arquivo e retorna uma referência (video_url) para recuperá-lo depois."""

    def path_for(self, video_url: str) -> Path:
        """Resolve a referência salva para um caminho local utilizável pelo pipeline."""

    def delete(self, video_url: str) -> None:
        """Remove o vídeo após a extração (retenção — ADR 0003)."""


class LocalStorage:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, fileobj: BinaryIO, filename: str) -> str:
        suffix = Path(filename).suffix
        video_url = f"{uuid.uuid4()}{suffix}"
        dest = self.base_dir / video_url
        with dest.open("wb") as out:
            shutil.copyfileobj(fileobj, out)
        return video_url

    def path_for(self, video_url: str) -> Path:
        return self.base_dir / video_url

    def delete(self, video_url: str) -> None:
        self.path_for(video_url).unlink(missing_ok=True)


def get_storage() -> Storage:
    return LocalStorage()
