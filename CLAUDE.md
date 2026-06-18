# wildrift-analizer

Coach pessoal de Wild Rift: o usuário sobe o vídeo da partida, o sistema extrai
dados (OCR + visão computacional), cruza com o meta atual (scraping diário) e
devolve um relatório narrativo gerado por LLM apontando erros de decisão
(rotação, visão, gestão de tempo) — não as estatísticas que o próprio jogo já
mostra.

Não existe API oficial da Riot para Wild Rift. Por isso a extração de dados é
feita assistindo ao vídeo, não consultando um servidor de partida.

## Como este projeto organiza contexto

- `docs/architecture.md` — visão geral do sistema, bloco por bloco.
- `docs/scope.md` — revisão da arquitetura e o que está dentro/fora do MVP.
- `docs/roadmap.md` — ordem de construção, fase por fase.
- `docs/data-model.md` — schema do Postgres.
- `docs/api.md` — contrato dos endpoints do FastAPI.
- `docs/decisions/` — ADRs: por que cada escolha técnica foi feita e quais
  riscos ela assume.
- `.claude/agents/` — subagentes especializados por área (scraper, pipeline de
  vídeo, API, frontend, análise via LLM, infra). Use-os em vez do agente
  genérico quando a tarefa cair claramente numa dessas áreas.

Antes de propor uma mudança de arquitetura, leia o ADR relevante em
`docs/decisions/` — se a decisão já foi tomada e o contexto não mudou, não
reabra a discussão sem motivo novo.

## Stack (resumo — ver `docs/architecture.md` para detalhes)

Frontend React/SvelteKit (Cloudflare Pages) → FastAPI (Railway/VPS) →
Redis/Celery → Workers (ffmpeg + PaddleOCR + YOLO) → PostgreSQL. Scrapers de
meta (Wild Legends, lolm.qq.com) rodam separados. LLM (Gemini Flash / Groq /
Claude) gera o relatório final.

A Fase 0 (ver `docs/scope.md`) simplifica isso para validar o pipeline antes
de construir a infraestrutura completa.
