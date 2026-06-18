from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas import MetaChampionOut, MetaPatchOut
from core.db import get_db
from core.models import MetaChampion, MetaPatch

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/champions", response_model=list[MetaChampionOut])
def list_champions(db: Session = Depends(get_db)) -> list[MetaChampion]:
    latest_patch = db.query(MetaPatch).order_by(MetaPatch.release_date.desc()).first()
    query = db.query(MetaChampion)
    if latest_patch:
        query = query.filter(MetaChampion.patch == latest_patch.patch_version)
    return query.order_by(MetaChampion.tier).all()


@router.get("/champions/{champion_name}", response_model=MetaChampionOut)
def get_champion(champion_name: str, db: Session = Depends(get_db)) -> MetaChampion:
    champion = (
        db.query(MetaChampion)
        .filter(MetaChampion.champion_name == champion_name)
        .order_by(MetaChampion.updated_at.desc())
        .first()
    )
    if champion is None:
        raise HTTPException(status_code=404, detail="Campeão não encontrado no meta")
    return champion


@router.get("/patch", response_model=MetaPatchOut)
def get_current_patch(db: Session = Depends(get_db)) -> MetaPatch:
    patch = db.query(MetaPatch).order_by(MetaPatch.release_date.desc()).first()
    if patch is None:
        raise HTTPException(status_code=404, detail="Nenhum patch registrado ainda")
    return patch
