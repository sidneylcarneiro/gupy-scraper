"""Caso de uso: salvar uma vaga no repositorio (camada de aplicacao)."""

from domain.entities.vaga import Vaga
from domain.repositories.vaga_repository import IVagaRepository


class SalvarVagaUseCase:
    """Orquestra a persistencia de uma vaga via o contrato IVagaRepository."""

    def __init__(self, repositorio: IVagaRepository):
        self._repositorio = repositorio

    def executar(self, vaga: Vaga) -> Vaga:
        """Salva a vaga informada e retorna a propria vaga."""
        self._repositorio.salvar(vaga)
        return vaga