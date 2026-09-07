"""Port para extratores de vagas (camada de aplicacao).

A aplicacao depende apenas deste contrato; a implementacao concreta
(Playwright) vive na camada de infraestrutura (Inversao de Dependencia).
"""

from typing import Protocol

from domain.entities.vaga import Vaga


class IExtratorDeVagas(Protocol):
    """Contrato dos extratores de vagas (listagem + detalhes)."""

    def extrair_vagas(self) -> list[Vaga]:
        """Extrai as vagas da listagem de busca."""
        ...

    def extrair_detalhes_vaga(self, url: str) -> str:
        """Extrai a descricao detalhada da pagina individual da vaga."""
        ...