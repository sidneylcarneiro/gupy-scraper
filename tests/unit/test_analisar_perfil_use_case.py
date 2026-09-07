"""Testes unitarios do AnalisarPerfilCandidatoUseCase (com fakes, custo zero)."""

from application.use_cases.analisar_perfil_candidato import AnalisarPerfilCandidatoUseCase


class AnalisadorFake:
    """Fake de IAnalisadorIA que registra a chamada e retorna um dict fixo."""

    def __init__(self, retorno: dict | None = None):
        self.retorno = retorno if retorno is not None else {"aderentes": [], "faltantes": []}
        self.chamadas: list[tuple[list[str], str]] = []

    def extrair_palavras_chave(self, descricao_vaga: str) -> list[str]:
        return []

    def analisar_perfil(self, vaga_keywords: list[str], perfil_candidato: str) -> dict:
        self.chamadas.append((list(vaga_keywords), perfil_candidato))
        return dict(self.retorno)


def test_deve_delegar_analise_de_perfil_ao_analisador():
    analisador = AnalisadorFake(
        retorno={"aderentes": ["Python"], "faltantes": ["Django"]}
    )
    use_case = AnalisarPerfilCandidatoUseCase(analisador=analisador)

    resultado = use_case.executar(
        vaga_keywords=["Python", "Django"], perfil_candidato="Dev Python com 5 anos"
    )

    assert resultado == {"aderentes": ["Python"], "faltantes": ["Django"]}
    assert analisador.chamadas == [(["Python", "Django"], "Dev Python com 5 anos")]


def test_deve_retornar_dict_vazio_quando_analisador_falha():
    analisador = AnalisadorFake(retorno={})
    use_case = AnalisarPerfilCandidatoUseCase(analisador=analisador)

    resultado = use_case.executar(vaga_keywords=["Python"], perfil_candidato="perfil")

    assert resultado == {}


def test_deve_propagar_retorno_completo_do_analisador():
    esperado = {
        "aderentes": ["Python", "Docker", "Clean Code"],
        "faltantes": ["AWS", "Kubernetes"],
    }
    use_case = AnalisarPerfilCandidatoUseCase(analisador=AnalisadorFake(retorno=esperado))

    resultado = use_case.executar(
        vaga_keywords=["Python", "Docker", "AWS", "Kubernetes", "Clean Code"],
        perfil_candidato="Backend Python",
    )

    assert resultado == esperado