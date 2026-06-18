# 0002 — Fase 0 sem fila/GPU antes de escalar

## Contexto
A arquitetura de longo prazo usa Redis + Celery para fila assíncrona e
workers com GPU (própria ou serverless) para o processamento pesado de
vídeo. Montar isso tudo antes de saber se o pipeline de extração + LLM
produz um relatório útil é gastar tempo e dinheiro numa hipótese ainda não
validada.

## Decisão
Fase 0 roda em um único processo: FastAPI recebe o upload e processa com
`BackgroundTasks` (sem fila separada), sem GPU (PaddleOCR roda aceitável em
CPU; YOLO fica fora da Fase 0 — ver ADR 0001). Só migra para Celery/Redis e
workers com GPU na Fase 1, depois que a Fase 0 validar o pipeline em
partidas reais (critério de saída em `docs/scope.md`).

## Consequências
- Processamento mais lento por partida na Fase 0 (aceitável para validação
  com poucos usuários — o próprio dev).
- Evita custo de Redis/GPU/infra distribuída antes de ter certeza de que o
  produto funciona.
- Migração para fila assíncrona na Fase 1 é trabalho conhecido e isolado:
  troca `BackgroundTasks` por `Celery.delay()`, sem reescrever a lógica de
  extração/análise.
