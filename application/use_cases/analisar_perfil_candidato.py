"""Caso de uso: analisar o perfil do candidato contra as keywords da vaga."""

from application.interfaces.analisador_ia_port import IAnalisadorIA


class AnalisarPerfilCandidatoUseCase:
    """Delega a analise de aderencia (match) entre vaga e candidato a IA."""

    def __init__(self, analisador: IAnalisadorIA):
        self._analisador = analisador

    def executar(self, vaga_keywords: list[str], perfil_candidato: str) -> dict:
        """Compara as keywords da vaga com o perfil e retorna o dict da IA.

        O dict contem as chaves 'aderentes' e 'faltantes'; em caso de falha
        do analisador, retorna um dict vazio.
        """
        return self._analisador.analisar_perfil(vaga_keywords, perfil_candidato)