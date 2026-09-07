"""Testes unitarios do adaptador LLMAnalisador (resposta simulada, sem rede)."""

from infrastructure.external_services.llm_analisador import LLMAnalisador


def test_deve_retornar_palavras_chave_simuladas():
    analisador = LLMAnalisador(api_key="chave-teste")

    resultado = analisador.extrair_palavras_chave("Descricao da vaga qualquer.")

    assert resultado == ["Python", "FastAPI", "Clean Architecture"]


def test_deve_ler_api_key_do_ambiente_quando_nao_informada(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "chave-do-env")

    analisador = LLMAnalisador()

    assert analisador.api_key == "chave-do-env"


def test_deve_preferir_api_key_informada_no_construtor(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "chave-do-env")

    analisador = LLMAnalisador(api_key="chave-explicita")

    assert analisador.api_key == "chave-explicita"