"""Extração de frames do vídeo via ffmpeg.

Requer o binário `ffmpeg` instalado no sistema — não é dependência Python.
Isolado em uma função fininha pra ser fácil de mockar em teste (subprocess).
"""

import subprocess
from pathlib import Path


def extract_frames(video_path: Path, out_dir: Path, fps: int = 1) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / "frame_%06d.png"
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            f"fps={fps}",
            "-y",
            str(pattern),
        ],
        check=True,
        capture_output=True,
    )
    return sorted(out_dir.glob("frame_*.png"))
