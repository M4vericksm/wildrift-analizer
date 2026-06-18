"""Rate limit de upload por usuário.

Fase 0: contador em memória do próprio processo — suficiente porque a API
roda em um único processo (sem fila/múltiplos workers, ver ADR 0002). Se a
API passar a rodar em múltiplos processos/réplicas, isso precisa virar um
contador compartilhado (Redis), porque cada processo teria seu próprio
estado e o limite deixaria de valer de fato.
"""

import time
from collections import defaultdict

_UPLOAD_TIMESTAMPS: dict[str, list[float]] = defaultdict(list)

MAX_UPLOADS_PER_WINDOW = 10
WINDOW_SECONDS = 3600


def is_rate_limited(user_id: str, now: float | None = None) -> bool:
    now = now if now is not None else time.time()
    cutoff = now - WINDOW_SECONDS
    timestamps = [t for t in _UPLOAD_TIMESTAMPS[user_id] if t > cutoff]
    _UPLOAD_TIMESTAMPS[user_id] = timestamps
    return len(timestamps) >= MAX_UPLOADS_PER_WINDOW


def record_upload(user_id: str, now: float | None = None) -> None:
    now = now if now is not None else time.time()
    _UPLOAD_TIMESTAMPS[user_id].append(now)
