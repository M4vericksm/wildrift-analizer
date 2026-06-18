# Modelo de dados (PostgreSQL)

Schema de referência para a arquitetura completa (`docs/architecture.md`). Na
Fase 0 (`docs/scope.md`) só `users`, `matches`, `timelines` e `analyses` são
necessárias — `events` pode nascer simplificada dentro de `analyses` até os
detectores de eventos macro existirem de fato.

```sql
users
  id, email, name, created_at

matches
  id, user_id, video_url, status, created_at,
  champion_played, role, result -- 'win' | 'loss'

timelines               -- uma linha por momento da partida
  id, match_id, timestamp_seconds,
  cs, gold, level, position_x, position_y

events                  -- eventos detectados (Fase 1+: posição via YOLO)
  id, match_id, timestamp_seconds,
  event_type,            -- 'death' | 'kill' | 'objective' | 'gank_ignored'
  data_json

analyses                -- relatórios gerados pelo LLM
  id, match_id, summary_markdown, top_mistakes_json,
  top_good_plays_json, llm_model_used, generated_at

meta_champions          -- dados raspados de Wild Legends + lolm.qq.com
  id, champion_name, patch, role, tier,
  winrate, pickrate, banrate,
  build_items_json, runes_json, skill_order_json,
  updated_at, source    -- 'wildlegends' | 'lolm_qq'

meta_patches
  id, patch_version, release_date, notes
```

`matches.status`: `pending` → `processing` → `ready` | `error`.
