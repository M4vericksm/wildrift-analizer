# API (FastAPI)

Contrato de referência para a arquitetura completa. Na Fase 0, `status`
ainda não precisa de fila — o próprio `BackgroundTasks` do FastAPI processa
e atualiza o registro no Postgres ao final.

```
POST /auth/login              login
POST /matches/upload          recebe vídeo, salva no storage, enfileira job
GET  /matches                 lista partidas do usuário
GET  /matches/{id}            detalhe + relatório
GET  /matches/{id}/status     'pending' | 'processing' | 'ready' | 'error'
GET  /meta/champions          tier list atual
GET  /meta/champions/{nome}   guia detalhado
GET  /meta/patch              info do patch atual
```

Validações obrigatórias no upload (ver ADR 0002 sobre escopo da Fase 0 e
`docs/scope.md` item 5): tipo de arquivo (vídeo), tamanho máximo, e rate
limit por usuário — sem isso o endpoint é o ponto mais fácil de abusar.
