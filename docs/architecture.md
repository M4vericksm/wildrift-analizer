# Arquitetura

Visão de longo prazo do sistema. Ver `docs/scope.md` para o que entra na Fase
0 e o que fica pra depois.

```
┌─────────────────┐
│   CELULAR       │
│  (você joga)    │
│   ↓ grava MP4   │
└────────┬────────┘
         │ upload
         ↓
┌──────────────────────────────────────────────┐
│         CLOUDFLARE (edge)                    │
│  - DNS / SSL / CDN                           │
│  - R2 (storage de vídeos)                    │
└────────┬─────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────┐
│         FRONTEND (Cloudflare Pages)          │
│  - React/SvelteKit — upload, login, relatório│
└────────┬─────────────────────────────────────┘
         │ API calls
         ↓
┌──────────────────────────────────────────────┐
│         BACKEND API (FastAPI)                │
│  - Recebe upload, enfileira job, serve dados │
└────────┬─────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────┐
│         FILA DE TRABALHO (Redis + Celery)    │
└────────┬─────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────┐
│         WORKERS (GPU ideal)                  │
│  - ffmpeg + PaddleOCR + YOLO + chamada LLM   │
└────────┬─────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────┐
│         POSTGRESQL                           │
│  - usuários, partidas, timelines, análises   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│         SCRAPERS (cron separado)             │
│  - Wild Legends (diário)                     │
│  - lolm.qq.com (diário, headless) — best-effort
└──────────────────────────────────────────────┘
```

## Blocos

### 1. Cliente
Só interface: login, upload de vídeo, lista de partidas, relatório. Nenhuma
lógica pesada no cliente. React/SvelteKit + Tailwind, hospedado em Cloudflare
Pages. Capacitor é opção futura para app Android nativo.

### 2. Edge / CDN (Cloudflare)
DNS, SSL automático, cache de assets estáticos, e R2 para storage de vídeo —
ver ADR 0003 sobre por que R2 em vez de S3 e sobre retenção dos arquivos.

### 3. Backend API (FastAPI)
Recebe upload, valida, sobe pro storage, cria registro no Postgres, enfileira
o job de processamento e serve os resultados. Ver `docs/api.md` para o
contrato de endpoints.

Fluxo de upload:
1. Cliente envia o vídeo.
2. API gera um id da partida, sobe o arquivo pro storage.
3. Cria registro no Postgres com `status='pending'`.
4. Enfileira o job de processamento (Fase 0: `BackgroundTasks`; Fase 1+:
   Celery — ver ADR 0002).
5. Responde com o id da partida; cliente faz polling de status.

### 4. Fila de trabalho (Redis + Celery) — Fase 1+
Desacopla "receber pedido" de "processar pedido", necessário porque o
processamento de vídeo não cabe no tempo de uma requisição HTTP. Ver ADR
0002 para por que isso só entra depois da Fase 0.

### 5. Workers
Pegam o vídeo do storage, extraem frames (ffmpeg), leem números do HUD
(PaddleOCR), detectam posição de campeões no minimapa (YOLO — Fase 1+, ver
ADR 0001), aplicam heurísticas para marcar eventos macro (mortes sem visão,
objetivo livre, gank ignorado), montam o JSON da partida e chamam o LLM para
gerar o relatório narrativo.

### 6. Banco de dados (PostgreSQL)
Ver `docs/data-model.md` para o schema completo (usuários, partidas,
timelines, eventos, análises, meta de campeões).

### 7. Scrapers de meta
Processo independente dos workers de análise, roda em cron diário:
- **Wild Legends** — fonte principal, sem bloqueio de IP conhecido.
- **lolm.qq.com** — fonte com dados mais "de ponta" (servidor chinês), mas
  best-effort: ver ADR 0004 sobre risco de bloqueio de IP e ToS.

### 8. Integração com LLM
Transforma a timeline estruturada + contexto de meta num relatório narrativo
em português, no formato: resumo, top erros com timestamp, padrões
repetidos, recomendação de ajuste. Ver ADR 0005 sobre escolha de provedor.

### 9. Observabilidade — Fase 1+
Sentry para erros, logs estruturados, uptime check. Não necessário até haver
usuários reais além do próprio dev.
