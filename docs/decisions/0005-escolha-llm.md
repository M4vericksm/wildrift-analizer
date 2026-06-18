# 0005 — Escolha de provedor de LLM

## Contexto
O relatório final é gerado por um LLM a partir da timeline estruturada +
contexto de meta. Existem opções gratuitas (Gemini Flash, Groq/Llama) e
pagas de maior qualidade (Claude Haiku/Sonnet).

## Decisão
Fase 0/1: usar um provedor gratuito (Gemini Flash ou Groq) para não ter
custo fixo durante a validação. Manter a chamada ao LLM isolada atrás de uma
interface simples (um único ponto que monta o prompt e recebe o texto) para
trocar de provedor sem tocar no resto do pipeline. Avaliar Claude
Haiku/Sonnet quando o produto tiver usuários reais e a qualidade da análise
precisar melhorar.

## Consequências
- Custo zero durante a fase de validação.
- Troca de provedor é uma mudança isolada, não um refactor do sistema.
- Qualidade da análise pode variar entre provedores — vale revisar a saída
  manualmente em algumas partidas antes de trocar de provedor em produção.
