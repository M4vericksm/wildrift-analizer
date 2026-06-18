"""Cria as tabelas no Postgres configurado em DATABASE_URL.

Fase 0 não usa Alembic (ver docs/scope.md) — quando o schema estabilizar e
houver dados reais em produção, migrar para Alembic em vez de
create_all/drop_all.
"""

from core.db import Base, engine
from core import models  # noqa: F401 — garante que os modelos sejam registrados


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas.")


if __name__ == "__main__":
    main()
