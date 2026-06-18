"""Geração do relatório narrativo via LLM.

Toda chamada a um provedor de LLM passa por esta única interface — ver
docs/decisions/0005-escolha-llm.md. Trocar de provedor é trocar a classe
retornada por get_llm_client(), não espalhar chamadas HTTP por outros
módulos.
"""

from typing import Protocol

import httpx

from core.config import settings

SYSTEM_PROMPT = """Você é um coach de Wild Rift experiente, com nível Challenger \
no servidor chinês. Analisa partidas focando em decisões macro: rotações, \
controle de visão, gestão de tempo, leitura de mapa. Responde em português \
brasileiro direto e objetivo, com timestamps específicos. Nunca repita \
estatísticas brutas (KDA, dano, ouro) que o próprio jogo já mostra — o foco \
é em decisões."""


class LLMClient(Protocol):
    model_name: str

    def generate_report(self, context: dict) -> str:
        """Recebe o contexto da partida (meta + timeline + eventos) e retorna
        o relatório em markdown, no formato: resumo, top erros com timestamp,
        padrões repetidos, recomendação de ajuste."""


def build_prompt(context: dict) -> str:
    return (
        f"[CONTEXTO DO META]\n{context.get('meta', '')}\n\n"
        f"[DADOS DA PARTIDA]\n{context.get('match_summary', '')}\n\n"
        f"[EVENTOS DETECTADOS]\n{context.get('events', '')}\n\n"
        "[TAREFA]\n"
        "Gere uma análise estruturada com:\n"
        "1. Resumo de 2 frases sobre a partida\n"
        "2. Top 3 erros mais impactantes (com timestamp, descrição, e o que "
        "deveria ter feito)\n"
        "3. Top 2 padrões que se repetiram\n"
        "4. 1 recomendação específica de ajuste pra próxima partida\n"
    )


class GeminiClient:
    model_name = "gemini-1.5-flash"
    _endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "{model}:generateContent"
    )

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def generate_report(self, context: dict) -> str:
        prompt = build_prompt(context)
        url = self._endpoint.format(model=self.model_name)
        body = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
        }
        response = httpx.post(
            url, params={"key": self._api_key}, json=body, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


class GroqClient:
    model_name = "llama-3.1-70b-versatile"
    _endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def generate_report(self, context: dict) -> str:
        prompt = build_prompt(context)
        response = httpx.post(
            self._endpoint,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def get_llm_client() -> LLMClient:
    if settings.llm_provider == "groq":
        return GroqClient(settings.groq_api_key)
    return GeminiClient(settings.gemini_api_key)
