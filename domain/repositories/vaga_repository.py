from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.vaga import Vaga

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