"""Use case: edit a saved search (alias + URL)."""

from application.use_cases.cadastrar_busca import normalizar_y_validar
from domain.entities.busca import Busca
from domain.repositories.busca_repository import IBuscaRepository


class BuscaNaoEncontradaError(Exception):
    """Signals that the requested search does not exist."""


class AtualizarBuscaUseCase:
    """Validates and updates the alias/URL of a saved search."""

    def __init__(self, repositorio: IBuscaRepository):
        self._repositorio = repositorio

    def executar(self, id_busca: int, apelido: str, url: str) -> Busca:
        """Updates the search; raises BuscaNaoEncontradaError if id does not exist."""
        apelido_normalizado, url_normalizada = normalizar_y_validar(apelido, url)
        busca = self._repositorio.atualizar(id_busca, apelido_normalizado, url_normalizada)
        if busca is None:
            raise BuscaNaoEncontradaError(f"Busca nao encontrada para o id: {id_busca}")
        return busca