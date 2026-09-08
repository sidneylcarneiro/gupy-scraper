"""Caso de uso: atualizar o status de uma vaga (funil Kanban)."""

from domain.entities.vaga import StatusVaga, Vaga
from domain.repositories.vaga_repository import IVagaRepository


class VagaNaoEncontradaError(Exception):
    """Sinaliza que a vaga informada nao existe no repositorio."""


class AtualizarStatusVagaUseCase:
    """Move uma vaga para um novo status do funil de candidaturas."""

    def __init__(self, repositorio: IVagaRepository):
        self._repositorio = repositorio

    def executar(self, id_vaga: int, novo_status: StatusVaga) -> Vaga:
        """Atualiza o status da vaga e retorna a entidade atualizada.

        Levanta VagaNaoEncontradaError quando o id nao existe.
        """
        vaga_atualizada = self._repositorio.atualizar_status(id_vaga, novo_status)
        if vaga_atualizada is None:
            raise VagaNaoEncontradaError(f"Vaga nao encontrada para o id: {id_vaga}")
        return vaga_atualizada