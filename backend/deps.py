"""Dependências compartilhadas das rotas.

Fase 0 não tem OAuth (isso é Fase 2 — docs/roadmap.md). Identifica o usuário
por e-mail num header simples e cria o registro se não existir, suficiente
para uso pessoal/validação. Trocar por JWT real é uma mudança isolada nesta
dependência, não nas rotas que a usam.
"""

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from core.models import User


def get_current_user(
    x_user_email: str = Header(...), db: Session = Depends(get_db)
) -> User:
    if not x_user_email or "@" not in x_user_email:
        raise HTTPException(status_code=401, detail="Header X-User-Email inválido")

    user = db.query(User).filter(User.email == x_user_email).first()
    if user is None:
        user = User(email=x_user_email, name=x_user_email.split("@")[0])
        db.add(user)
        db.commit()
    return user
