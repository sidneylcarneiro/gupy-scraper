"""Port para repositorios de buscas salvas (camada de dominio)."""

from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.busca import Busca


class IBuscaRepository(ABC):
    """Interface para o repositorio de buscas salvas."""

    @abstractmethod
    def salvar(self, busca: Busca) -> Busca:
        """Salva uma busca (com apelido) e retorna a entidade persistida."""
        pass

    @abstractmethod
    def listar(self) -> list[Busca]:
        """Retorna todas as buscas salvas, ordenadas por apelido."""
        pass

    @abstractmethod
    def buscar_por_id(self, id_busca: int) -> Optional[Busca]:
        """Busca uma busca pelo id. Retorna None quando nao encontrada."""
        pass

    @abstractmethod
    def remover(self, id_busca: int) -> None:
        """Remove a busca pelo id."""
        pass

    @abstractmethod
    def atualizar(self, id_busca: int, apelido: str, url: str) -> Optional[Busca]:
        """Updates the alias and URL of a search by id. Returns None if not found."""
        pass