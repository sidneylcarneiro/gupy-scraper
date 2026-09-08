"""Caso de uso: buscar uma vaga pelo id (pagina de detalhes)."""

from application.use_cases.atualizar_status_vaga import VagaNaoEncontradaError  # noqa: F401 (reexporta)
from domain.entities.vaga import Vaga
from domain.repositories.vaga_repository import IVagaRepository

__all__ = ["BuscarVagaPorIdUseCase", "VagaNaoEncontradaError"]


class BuscarVagaPorIdUseCase:
    """Recupera uma vaga unica pelo identificador."""

    def __init__(self, repositorio: IVagaRepository):
        self._repositorio = repositorio

    def executar(self, id_vaga: int) -> Vaga:
        """Retorna a vaga encontrada; levanta VagaNaoEncontradaError caso contrario."""
        vaga = self._repositorio.buscar_por_id(id_vaga)
        if vaga is None:
            raise VagaNaoEncontradaError(f"Vaga nao encontrada para o id: {id_vaga}")
        return vaga