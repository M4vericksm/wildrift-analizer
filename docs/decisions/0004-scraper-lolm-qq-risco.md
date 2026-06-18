# 0004 — Scraper do lolm.qq.com como best-effort

## Contexto
lolm.qq.com tem os dados de meta mais "de ponta" (servidor chinês), mas: (a)
pode bloquear IPs fora da China, exigindo proxy residencial ou VPS em
Hong Kong/Singapura; (b) scraping de terceiro carrega risco de ToS. O Wild
Legends já cobre o essencial em português, sem esses riscos.

## Decisão
Tratar o scraper do lolm.qq.com como fonte best-effort, não como dependência
crítica do produto. O sistema deve funcionar plenamente só com os dados do
Wild Legends; o lolm.qq.com entra como enriquecimento quando disponível, e
fica fora do escopo da Fase 0 (ver `docs/scope.md`).

## Consequências
- Nenhuma funcionalidade do produto fica bloqueada se o lolm.qq.com começar
  a bloquear o IP do scraper ou mudar de estrutura.
- Quando esse scraper for implementado (Fase 2), isolar falhas dele do
  pipeline principal (cron separado, sem afetar `meta_champions` já populada
  pelo Wild Legends).
