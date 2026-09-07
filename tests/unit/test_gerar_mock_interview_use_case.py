"""Testes unitarios do GerarMockInterviewUseCase (com fakes, custo zero)."""

from application.use_cases.gerar_mock_interview import GerarMockInterviewUseCase


class AnalisadorFake:
    """Fake de IAnalisadorIA que registra a chamada e retorna perguntas fixas."""

    def __init__(self, retorno: list[str] | None = None):
        self.retorno = retorno if retorno is not None else []
        self.chamadas: list[tuple[str, list[str]]] = []

    def extrair_palavras_chave(self, descricao_vaga: str) -> list[str]:
        return []

    def analisar_perfil(self, vaga_keywords: list[str], perfil_candidato: str) -> dict:
        return {}

    def gerar_perguntas_entrevista(self, titulo_vaga: str, habilidades_faltantes: list[str]) -> list[str]:
        self.chamadas.append((titulo_vaga, list(habilidades_faltantes)))
        return list(self.retorno)


def test_deve_delegar_geracao_de_perguntas_ao_analisador():
    perguntas_fixas = [
        "Como voce estruturaria testes automatizados?",
        "Descreva sua experiencia com AWS.",
    ]
    analisador = AnalisadorFake(retorno=perguntas_fixas)
    use_case = GerarMockInterviewUseCase(analisador=analisador)

    resultado = use_case.executar(
        titulo_vaga="Dev Python Senior", habilidades_faltantes=["AWS", "Testes"]
    )

    assert resultado == perguntas_fixas
    assert analisador.chamadas == [("Dev Python Senior", ["AWS", "Testes"])]


def test_deve_retornar_lista_vazia_quando_analisador_falha():
    use_case = GerarMockInterviewUseCase(analisador=AnalisadorFake(retorno=[]))

    resultado = use_case.executar(titulo_vaga="Dev Python", habilidades_faltantes=["AWS"])

    assert resultado == []


def test_deve_propagar_todas_as_perguntas_geradas():
    esperado = [f"Pergunta {i}" for i in range(1, 6)]
    use_case = GerarMockInterviewUseCase(analisador=AnalisadorFake(retorno=esperado))

    resultado = use_case.executar(titulo_vaga="Backend Python", habilidades_faltantes=["React"])

    assert resultado == esperado