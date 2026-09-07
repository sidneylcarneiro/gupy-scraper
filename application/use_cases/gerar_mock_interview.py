"""Caso de uso: gerar mock interview para as habilidades faltantes do candidato."""

from application.interfaces.analisador_ia_port import IAnalisadorIA


class GerarMockInterviewUseCase:
    """Delega a geracao de perguntas de entrevista simulada a IA."""

    def __init__(self, analisador: IAnalisadorIA):
        self._analisador = analisador

    def executar(self, titulo_vaga: str, habilidades_faltantes: list[str]) -> list[str]:
        """Retorna as perguntas de entrevista geradas pela IA.

        Em caso de falha do analisador, retorna uma lista vazia.
        """
        return self._analisador.gerar_perguntas_entrevista(titulo_vaga, habilidades_faltantes)