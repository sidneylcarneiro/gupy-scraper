"""Adaptador de LLM (DeepSeek via SDK da OpenAI) para analise de vagas.

A API do DeepSeek e nativamente compativel com o SDK da OpenAI: basta apontar
a base_url para https://api.deepseek.com e usar a chave configurada no .env
(LLM_API_KEY).
"""

import json
import os
from typing import Optional

from openai import OpenAI

BASE_URL_DEEPSEEK = "https://api.deepseek.com"


class LLMAnalisador:
    """Implementa IAnalisadorIA extraindo palavras-chave via LLM (DeepSeek)."""

    def __init__(self, api_key: Optional[str] = None, modelo: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.modelo = modelo

        if not self.api_key:
            raise ValueError("API Key do LLM não configurada.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=BASE_URL_DEEPSEEK,
        )

    def extrair_palavras_chave(self, descricao_vaga: str) -> list[str]:
        """Extrai palavras-chave tecnicas e comportamentais da descricao.

        Retorna lista vazia quando a descricao e vazia ou quando a chamada ao
        LLM falha, para nao quebrar o fluxo do caso de uso.
        """
        if not descricao_vaga.strip():
            return []

        prompt = f'''
        Você é um especialista em recrutamento tech. Analise a seguinte descrição de vaga e extraia as principais palavras-chave técnicas e comportamentais (ex: tecnologias, frameworks, metodologias, soft skills).
        Retorne APENAS um array JSON válido contendo as strings. Exemplo: ["Python", "FastAPI", "Clean Architecture"].
        Não inclua markdown ou qualquer outro texto na resposta.
        
        Descrição da vaga:
        {descricao_vaga}
        '''

        try:
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            resposta_texto = response.choices[0].message.content.strip()

            # Limpeza caso a IA insira blocos de codigo markdown
            if resposta_texto.startswith("```json"):
                resposta_texto = resposta_texto[7:-3].strip()
            elif resposta_texto.startswith("```"):
                resposta_texto = resposta_texto[3:-3].strip()

            return json.loads(resposta_texto)
        except Exception as erro:
            print(f"Erro ao analisar com LLM: {erro}")
            return []