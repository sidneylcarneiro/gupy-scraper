"""Caso de uso: analisar a aderencia de um candidato a uma vaga via IA."""

from application.interfaces.analisador_ia_port import IAnalisadorIA
from domain.repositories.vaga_repository import IVagaRepository


class VagaNaoEncontradaError(Exception):
    """Sinaliza que a vaga informada nao existe no repositorio."""


class AnalisarAderenciaUseCase:
    """Busca a vaga pelo URL e extrai as palavras-chave da descricao via IA."""

    def __init__(self, repositorio: IVagaRepository, analisador: IAnalisadorIA):
        self._repositorio = repositorio
        self._analisador = analisador

    def executar(self, url_vaga: str) -> list[str]:
        """Busca a vaga e retorna as palavras-chave extraidas pela IA.

        Levanta VagaNaoEncontradaError quando a URL nao existe no repositorio,
        sem acionar o analisador de IA desnecessariamente.
        """
        vaga = self._repositorio.buscar_por_url(url_vaga)
        if vaga is None:
            raise VagaNaoEncontradaError(f"Vaga nao encontrada para a URL: {url_vaga}")
        return self._analisador.extrair_palavras_chave(vaga.descricao)