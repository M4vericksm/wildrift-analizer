from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.deps import get_current_user
from backend.schemas import MatchDetailOut, MatchOut, MatchStatusOut
from backend.services.pipeline import process_match
from backend.services.rate_limit import is_rate_limited, record_upload
from backend.services.storage import Storage, get_storage
from core.config import settings
from core.db import get_db
from core.models import Match, MatchStatus, User

router = APIRouter(prefix="/matches", tags=["matches"])

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv"}


@router.post("/upload", response_model=MatchOut, status_code=202)
def upload_match(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    champion_played: str | None = Form(default=None),
    role: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    storage: Storage = Depends(get_storage),
) -> Match:
    if is_rate_limited(user.id):
        raise HTTPException(status_code=429, detail="Limite de uploads por hora excedido")

    suffix = _validate_filename(file.filename)
    _validate_size(file)

    video_url = storage.save(file.file, f"upload{suffix}")
    record_upload(user.id)

    match = Match(
        user_id=user.id,
        video_url=video_url,
        status=MatchStatus.pending,
        champion_played=champion_played,
        role=role,
    )
    db.add(match)
    db.commit()

    background_tasks.add_task(process_match, match.id, db, storage)
    return match


def _validate_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome")
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensão não suportada. Use uma de: {sorted(ALLOWED_VIDEO_EXTENSIONS)}",
        )
    return suffix


def _validate_size(file: UploadFile) -> None:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Vídeo excede o limite de {settings.max_upload_mb}MB",
        )


@router.get("", response_model=list[MatchOut])
def list_matches(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Match]:
    return db.query(Match).filter(Match.user_id == user.id).order_by(Match.created_at.desc()).all()


@router.get("/{match_id}", response_model=MatchDetailOut)
def get_match(
    match_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Match:
    match = _get_owned_match(match_id, db, user)
    return match


@router.get("/{match_id}/status", response_model=MatchStatusOut)
def get_match_status(
    match_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Match:
    return _get_owned_match(match_id, db, user)


def _get_owned_match(match_id: str, db: Session, user: User) -> Match:
    match = db.get(Match, match_id)
    if match is None or match.user_id != user.id:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return match
