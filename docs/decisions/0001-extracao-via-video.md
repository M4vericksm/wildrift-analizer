# 0001 — Extração via vídeo, sem API da Riot

## Contexto
A Riot não disponibiliza API pública para Wild Rift. Não há como consultar
dados de partida em um servidor oficial.

## Decisão
Extrair os dados assistindo ao vídeo gravado pelo próprio jogador: OCR no
HUD para CS/gold/level/KDA, leitura do kill feed por texto, e (Fase 2) YOLO
para posição de campeões no minimapa.

## Consequências
- É a única via viável para esse produto — não há alternativa com API.
- OCR e kill feed por texto são baratos de construir e validar; YOLO para
  minimapa exige treinar um modelo do zero (não existe pronto para Wild
  Rift), o que é um projeto de ML por si só. Ver ADR 0002: por isso o YOLO
  fica fora da Fase 0.
- Qualidade da extração depende de resolução/qualidade do vídeo gravado pelo
  usuário — vale documentar requisitos mínimos de gravação assim que isso
  virar um problema real.
