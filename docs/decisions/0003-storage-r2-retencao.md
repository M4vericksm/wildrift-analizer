# 0003 — Storage R2 e retenção de vídeo

## Contexto
Vídeos de partida (~500MB) são pesados. Em S3, o egress (download pelo
worker) custa caro pra esse volume. Cloudflare R2 tem egress grátis, o que é
decisivo quando o vídeo precisa ser baixado pelo worker pra processar.

## Decisão
Usar Cloudflare R2 para storage de vídeo (Fase 1+; Fase 0 usa storage local
ou bucket simples — ver ADR 0002). Apagar o arquivo de vídeo do storage
depois que a extração terminar, guardando permanentemente só o JSON da
timeline/eventos e a análise gerada — não o vídeo original.

## Consequências
- Custo de storage previsível mesmo com volume crescente de partidas, porque
  o vídeo não se acumula indefinidamente.
- Se for necessário reprocessar uma partida (ex.: bug no OCR), o vídeo
  original já não existe — aceitável, dado que o objetivo é o relatório, não
  o vídeo em si. Se isso virar problema, considerar uma janela de retenção
  (ex.: 7 dias) em vez de exclusão imediata.
