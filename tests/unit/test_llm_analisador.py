"""Testes unitarios do LLMAnalisador (client OpenAI mockado, sem rede)."""

from unittest.mock import MagicMock, patch

import pytest

from infrastructure.external_services.llm_analisador import BASE_URL_DEEPSEEK, LLMAnalisador

MODULO = "infrastructure.external_services.llm_analisador.OpenAI"


def _resposta_llm(conteudo: str) -> MagicMock:
    resposta = MagicMock()
    resposta.choices[0].message.content = conteudo
    return resposta


def test_deve_extrair_palavras_chave_via_llm():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm('["Python", "Docker"]')

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.extrair_palavras_chave("Vaga com Python e Docker.")

    assert resultado == ["Python", "Docker"]
    mock_openai_cls.assert_called_once_with(api_key="chave-teste", base_url=BASE_URL_DEEPSEEK)

    kwargs = cliente.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "deepseek-chat"
    assert kwargs["temperature"] == 0.1
    assert kwargs["messages"][0]["role"] == "user"
    assert "Vaga com Python e Docker." in kwargs["messages"][0]["content"]


def test_deve_limpar_bloco_markdown_json_da_resposta():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm('```json\n["Python"]\n```')

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.extrair_palavras_chave("descricao")

    assert resultado == ["Python"]


def test_deve_limpar_bloco_markdown_simples_da_resposta():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm('```\n["FastAPI"]\n```')

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.extrair_palavras_chave("descricao")

    assert resultado == ["FastAPI"]


def test_deve_retornar_lista_vazia_quando_llm_falha():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.side_effect = RuntimeError("API fora do ar")

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.extrair_palavras_chave("descricao")

    assert resultado == []


def test_deve_retornar_vazio_sem_chamar_llm_para_descricao_vazia():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.extrair_palavras_chave("   \n\t")

    assert resultado == []
    cliente.chat.completions.create.assert_not_called()


def test_deve_lancar_valueerror_quando_api_key_ausente(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    with pytest.raises(ValueError, match="API Key do LLM"):
        LLMAnalisador()


def test_deve_ler_api_key_do_ambiente_quando_nao_informada(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "chave-do-env")

    with patch(MODULO):
        analisador = LLMAnalisador()

    assert analisador.api_key == "chave-do-env"


def test_deve_preferir_api_key_informada_no_construtor(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "chave-do-env")

    with patch(MODULO):
        analisador = LLMAnalisador(api_key="chave-explicita")

    assert analisador.api_key == "chave-explicita"


def test_deve_analisar_perfil_e_retornar_aderentes_e_faltantes():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm(
            '{"aderentes": ["Python"], "faltantes": ["AWS"]}'
        )

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.analisar_perfil(
            vaga_keywords=["Python", "AWS"], perfil_candidato="Dev Python"
        )

    assert resultado == {"aderentes": ["Python"], "faltantes": ["AWS"]}

    kwargs = cliente.chat.completions.create.call_args.kwargs
    conteudo = kwargs["messages"][0]["content"]
    assert kwargs["model"] == "deepseek-chat"
    assert kwargs["temperature"] == 0.1
    assert '"aderentes"' in conteudo
    assert "Python" in conteudo
    assert "AWS" in conteudo


def test_deve_normalizar_resposta_do_perfil_sem_chaves_completas():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm('{"aderentes": ["Docker"]}')

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.analisar_perfil(vaga_keywords=["Docker"], perfil_candidato="DevOps")

    assert resultado == {"aderentes": ["Docker"], "faltantes": []}


def test_deve_retornar_dict_vazio_quando_analise_de_perfil_falha():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.side_effect = RuntimeError("API fora do ar")

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.analisar_perfil(vaga_keywords=["Python"], perfil_candidato="perfil")

    assert resultado == {}


def test_deve_retornar_dict_vazio_sem_chamar_llm_para_entradas_vazias():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value

        analisador = LLMAnalisador(api_key="chave-teste")

        assert analisador.analisar_perfil(vaga_keywords=[], perfil_candidato="perfil") == {}
        assert analisador.analisar_perfil(vaga_keywords=["Python"], perfil_candidato="   ") == {}

    cliente.chat.completions.create.assert_not_called()


def test_deve_gerar_perguntas_de_entrevista_via_llm():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm(
            '["P1?", "P2?", "P3?", "P4?", "P5?"]'
        )

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.gerar_perguntas_entrevista(
            titulo_vaga="Dev Python", habilidades_faltantes=["AWS", "React"]
        )

    assert resultado == ["P1?", "P2?", "P3?", "P4?", "P5?"]

    kwargs = cliente.chat.completions.create.call_args.kwargs
    conteudo = kwargs["messages"][0]["content"]
    assert kwargs["model"] == "deepseek-chat"
    assert kwargs["temperature"] == 0.1
    assert "Dev Python" in conteudo
    assert "AWS" in conteudo


def test_deve_limpar_bloco_markdown_json_das_perguntas():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm(
            '```json\n["P1?", "P2?"]\n```'
        )

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.gerar_perguntas_entrevista(
            titulo_vaga="Dev Python", habilidades_faltantes=["AWS"]
        )

    assert resultado == ["P1?", "P2?"]


def test_deve_retornar_lista_vazia_quando_geracao_de_perguntas_falha():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.side_effect = RuntimeError("API fora do ar")

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.gerar_perguntas_entrevista(
            titulo_vaga="Dev Python", habilidades_faltantes=["AWS"]
        )

    assert resultado == []


def test_deve_retornar_lista_vazia_quando_resposta_nao_e_array():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value
        cliente.chat.completions.create.return_value = _resposta_llm('{"pergunta": "P1?"}')

        analisador = LLMAnalisador(api_key="chave-teste")
        resultado = analisador.gerar_perguntas_entrevista(
            titulo_vaga="Dev Python", habilidades_faltantes=["AWS"]
        )

    assert resultado == []


def test_deve_retornar_vazio_sem_chamar_llm_para_entradas_vazias_de_interview():
    with patch(MODULO) as mock_openai_cls:
        cliente = mock_openai_cls.return_value

        analisador = LLMAnalisador(api_key="chave-teste")

        assert analisador.gerar_perguntas_entrevista(titulo_vaga="", habilidades_faltantes=["AWS"]) == []
        assert analisador.gerar_perguntas_entrevista(titulo_vaga="Dev", habilidades_faltantes=[]) == []

    cliente.chat.completions.create.assert_not_called()