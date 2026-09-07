"""Adaptador de LLM para analise de vagas (camada de infraestrutura).

Por enquanto retorna palavras-chave simuladas (mock). A estrutura ja esta
preparada para plugar um provedor real (OpenAI/Anthropic/Gemini etc.) usando
a chave de API configurada no .env (LLM_API_KEY).
"""

import os
from typing import Optional


class LLMAnalisador:
    """Implementa IAnalisadorIA com resposta simulada (fase de mock)."""

    PALAVRAS_CHAVE_SIMULADAS = ["Python", "FastAPI", "Clean Architecture"]

    def __init__(self, api_key: Optional[str] = None, modelo: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.modelo = modelo

    def extrair_palavras_chave(self, descricao_vaga: str) -> list[str]:
        """Extrai as palavras-chave da descricao (simulado por enquanto).

        TODO(Fase 4): substituir pela chamada real ao provedor de LLM usando
        self.api_key e self.modelo.
        """
        if not descricao_vaga:
            return []
        return list(self.PALAVRAS_CHAVE_SIMULADAS)