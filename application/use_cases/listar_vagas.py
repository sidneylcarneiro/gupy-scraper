"""Caso de uso: listar todas as vagas persistidas."""

from domain.entities.vaga import Vaga
from domain.repositories.vaga_repository import IVagaRepository


class ListarVagasUseCase:
    """Retorna todas as vagas do repositorio para exibicao no dashboard."""

    def __init__(self, repositorio: IVagaRepository):
        self._repositorio = repositorio

    def executar(self) -> list[Vaga]:
        """Retorna a lista completa de vagas."""
        return self._repositorio.listar_todas()