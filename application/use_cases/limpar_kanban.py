"""Caso de uso: limpar o Kanban descartando todas as vagas em processo."""

from domain.entities.vaga import StatusVaga
from domain.repositories.vaga_repository import IVagaRepository

STATUS_EM_PROCESSO = frozenset(
    {
        StatusVaga.ATIVA,
        StatusVaga.CANDIDATURA_ENVIADA,
        StatusVaga.EM_ANDAMENTO,
        StatusVaga.REJEITADA,
        StatusVaga.CONTRATADA,
    }
)


class LimparKanbanUseCase:
    """Descarta todas as vagas em processo, esvaziando o Kanban."""

    def __init__(self, repositorio: IVagaRepository):
        self._repositorio = repositorio

    def executar(self) -> int:
        """Move todas as vagas em processo para DESCARTADA.

        Retorna a quantidade de vagas afetadas. Vagas NOVA (triagem) nao
        sao tocadas.
        """
        quantidade_descartadas = 0
        for vaga in self._repositorio.listar_todas():
            if vaga.status in STATUS_EM_PROCESSO:
                self._repositorio.atualizar_status(vaga.id, StatusVaga.DESCARTADA)
                quantidade_descartadas += 1
        return quantidade_descartadas