# Escopo

## Revisão: esse é o melhor caminho?

A arquitetura de longo prazo está bem desenhada e as decisões fortes (vídeo em
vez de API da Riot, fila assíncrona, R2 em vez de S3, GPU serverless pro MVP)
fazem sentido — ver `docs/decisions/`. O risco não está na escolha de
tecnologia, está em construir as dez peças ao mesmo tempo antes de validar a
peça mais incerta: **a extração de dados do vídeo é boa o suficiente pra gerar
um relatório útil?**

Ajustes recomendados antes de começar a construir:

1. **YOLO pro minimapa é o maior risco do projeto, não um item de checklist.**
   Não existe modelo pronto pra Wild Rift — seria preciso rotular dataset e
   treinar do zero, o que é um projeto de ML por si só. Recomendo tirar do
   MVP e validar primeiro só com OCR do HUD + kill feed (texto), que já cobre
   a maioria dos eventos do prompt de exemplo (mortes, dragão, baron, ace).
2. **Celery + Redis + worker GPU desde o dia 1 é infraestrutura demais antes
   de saber se o produto funciona.** Uma Fase 0 com tudo em um único processo
   (FastAPI + `BackgroundTasks`, sem fila separada, sem GPU) responde a
   pergunta certa primeiro: o OCR lê os números certos, e o LLM escreve uma
   análise que faz sentido? Só then vale migrar para fila assíncrona e GPU.
3. **lolm.qq.com pode bloquear IP fora da China e tem risco de ToS ao
   raspar.** Tratar como fonte best-effort, não como dependência crítica — o
   Wild Legends já cobre o essencial em português.
4. **Vídeo de 500MB por partida acumula rápido.** Definir retenção: apagar o
   MP4 do storage depois de extrair os dados, guardando só o JSON da
   timeline, evita custo de storage crescendo sem limite.
5. **Falta validação/limite no upload** (tipo de arquivo, tamanho máximo,
   rate limit por usuário) — sem isso o endpoint de upload é o ponto mais
   fácil de abusar.

Nenhum desses pontos invalida a arquitetura de longo prazo — ela é o destino
certo. A mudança é a ordem: validar o pipeline de extração + LLM primeiro, com
o mínimo de infraestrutura, e só depois construir o resto.

## Dentro do escopo (Fase 0 — walking skeleton)

- Upload de vídeo (storage simples, sem R2 ainda)
- Extração: ffmpeg + PaddleOCR no HUD (CS, gold, level, KDA) + leitura de
  kill feed por texto
- Heurísticas simples em Python pra marcar eventos macro (sem YOLO/minimapa)
- 1 chamada de LLM (Gemini Flash, free tier) gerando o relatório no formato
  já desenhado no prompt de exemplo
- Front mínimo (ou retorno em JSON/Markdown) pra visualizar o relatório
- Scraper do Wild Legends rodando 1x/dia, alimentando o contexto de meta do
  prompt

## Fora do escopo por agora (Fase 1+)

- YOLO/minimapa, detecção de posição de campeões
- Fila Celery/Redis, múltiplos workers
- Scraper do lolm.qq.com
- R2, Cloudflare Pages, deploy distribuído
- Auth completo (OAuth), multi-usuário em produção
- App mobile via Capacitor
- Observabilidade (Sentry, Grafana)

## Critério de saída da Fase 0

Rodar em 5-10 partidas reais e decidir: o OCR captura os números certos? Os
eventos que o LLM aponta correspondem ao que de fato aconteceu na partida? Se
sim, vale investir no resto da arquitetura descrita em `docs/architecture.md`.
Se não, o problema é mais barato de descobrir aqui do que depois de montar
fila, GPU e storage distribuído.
