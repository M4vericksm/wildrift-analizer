# Roadmap

Ordem revisada para reduzir risco: validar o pipeline de extração + LLM
antes de investir em infraestrutura de fila/GPU/storage distribuído. Ver
`docs/scope.md` para a justificativa completa.

## Fase 0 — walking skeleton (valida a ideia)
1. Scraper do Wild Legends + tabela `meta_champions` básica
2. Endpoint de upload (FastAPI, storage local/bucket simples) +
   `BackgroundTasks` (sem Celery/Redis ainda)
3. ffmpeg + PaddleOCR no HUD → timeline simples (sem YOLO)
4. Heurísticas simples em Python pra marcar eventos macro a partir da
   timeline + kill feed por texto
5. Integração com LLM (Gemini Flash) gerando o relatório
6. Rodar em 5-10 partidas reais e avaliar contra o critério de saída em
   `docs/scope.md`

## Fase 1 — sai do walking skeleton (se a Fase 0 validar)
7. Frontend mínimo (React/SvelteKit) consumindo a API
8. Migra storage de vídeo pra Cloudflare R2, com retenção (apaga vídeo após
   extrair os dados — ADR 0003)
9. Migra processamento pra fila assíncrona (Redis + Celery), workers
   separados da API

## Fase 2 — escala e profundidade
10. YOLO treinado pra minimapa + heurísticas macro com posição (ADR 0001)
11. Scraper do lolm.qq.com (best-effort, ADR 0004)
12. Auth completo (OAuth), app mobile via Capacitor, observabilidade
    (Sentry, Grafana)

Cada fase entrega algo funcionando de ponta a ponta — não é preciso esperar
a fase inteira pra testar.
