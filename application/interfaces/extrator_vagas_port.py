"""Port para extratores de vagas (camada de aplicacao).

A aplicacao depende apenas deste contrato; a implementacao concreta
(Playwright) vive na camada de infraestrutura (Inversao de Dependencia).
"""

from typing import Protocol, runtime_checkable

from domain.entities.vaga import Vaga


@runtime_checkable
class IExtratorDeVagas(Protocol):
    """Contrato dos extratores de vagas (listagem + detalhes)."""

    def extrair_vagas(self, url_busca: str) -> list[Vaga]:
        """Extrai as vagas da listagem de busca informada."""
        ...

    def extrair_detalhes_vaga(self, url: str) -> str:
        """Extrai a descricao detalhada da pagina individual da vaga."""
        ...

    def fechar(self) -> None:
        """Libera os recursos do navegador (browser/aba), quando houver."""
        ...