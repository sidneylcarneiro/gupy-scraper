"""Port para servicos de analise por IA (camada de aplicacao).

A aplicacao depende apenas deste contrato; a implementacao concreta (LLM)
vive na camada de infraestrutura (Inversao de Dependencia).
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class IAnalisadorIA(Protocol):
    """Contrato dos analisadores de descricao de vaga por IA."""

    def extrair_palavras_chave(self, descricao_vaga: str) -> list[str]:
        """Extrai as palavras-chave tecnicas da descricao da vaga."""
        ...

    def analisar_perfil(self, vaga_keywords: list[str], perfil_candidato: str) -> dict:
        """Compara as palavras-chave da vaga com o perfil do candidato.

        Retorna dict com as chaves 'aderentes' e 'faltantes'.
        """
        ...

    def gerar_perguntas_entrevista(self, titulo_vaga: str, habilidades_faltantes: list[str]) -> list[str]:
        """Gera perguntas de mock interview focadas nas habilidades faltantes."""
        ...