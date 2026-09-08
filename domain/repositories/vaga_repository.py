from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.vaga import StatusVaga, Vaga


class IVagaRepository(ABC):
    """Interface para o repositório de Vagas."""

    @abstractmethod
    def salvar(self, vaga: Vaga) -> None:
        """Salva uma nova vaga no banco de dados."""
        pass

    @abstractmethod
    def buscar_por_url(self, url: str) -> Optional[Vaga]:
        """Busca uma vaga pela sua URL única. Retorna None quando não encontrada."""
        pass

    @abstractmethod
    def listar_todas(self) -> list[Vaga]:
        """Retorna todas as vagas persistidas."""
        pass

    @abstractmethod
    def atualizar_status(self, id_vaga: int, status: StatusVaga) -> Optional[Vaga]:
        """Atualiza o status da vaga pelo id. Retorna None quando não encontrada."""
        pass

    @abstractmethod
    def buscar_por_id(self, id_vaga: int) -> Optional[Vaga]:
        """Busca uma vaga pelo id. Retorna None quando não encontrada."""
        pass