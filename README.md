# wildrift-analizer

Coach pessoal de Wild Rift: sobe o vídeo da partida, recebe um relatório
narrativo apontando erros de decisão, cruzado com o meta atual.

Veja `CLAUDE.md` e `docs/` para arquitetura, escopo, roadmap e decisões.

## Rodando a Fase 0 localmente

Requer Python 3.11+, Docker (Postgres) e `ffmpeg` no PATH (extração de
frames — `docs/decisions/0002-fase-0-sem-fila-sem-gpu.md`).

```bash
docker compose up -d                  # Postgres
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                  # preencher GEMINI_API_KEY (ou GROQ_API_KEY)
python scripts/init_db.py             # cria as tabelas (sem Alembic na Fase 0)
uvicorn backend.main:app --reload
python -m scrapers.wild_legends       # popula meta_champions
```

Testes (não exigem Postgres/ffmpeg/rede — usam SQLite e fixtures locais):

```bash
pytest
```

`scrapers/wild_legends.py` ainda tem os seletores de HTML não calibrados
contra o site real (ambiente de desenvolvimento sem acesso de rede a
wildlegends.net no momento em que foi escrito) — ver aviso no topo do
arquivo antes de rodar em produção.
