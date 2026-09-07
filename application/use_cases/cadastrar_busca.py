"""Caso de uso: cadastrar uma busca da Gupy com apelido."""

from domain.entities.busca import Busca
from domain.repositories.busca_repository import IBuscaRepository

PREFIXO_URL_GUPY = "https://portal.gupy.io/"


class ApelidoInvalidoError(Exception):
    """Sinaliza que o apelido informado e vazio."""


class URLInvalidaError(Exception):
    """Sinaliza que a URL nao pertence ao portal da Gupy."""


class CadastrarBuscaUseCase:
    """Valida e persiste uma busca nomeada pelo usuario."""

    def __init__(self, repositorio: IBuscaRepository):
        self._repositorio = repositorio

    def executar(self, apelido: str, url: str) -> Busca:
        """Valida os dados e salva a busca no repositorio."""
        apelido_normalizado = (apelido or "").strip()
        if not apelido_normalizado:
            raise ApelidoInvalidoError("O apelido da busca e obrigatorio.")

        url_normalizada = (url or "").strip()
        if not url_normalizada.startswith(PREFIXO_URL_GUPY):
            raise URLInvalidaError("A URL deve pertencer ao portal da Gupy (https://portal.gupy.io/).")

        busca = Busca(apelido=apelido_normalizado, url=url_normalizada)
        return self._repositorio.salvar(busca)