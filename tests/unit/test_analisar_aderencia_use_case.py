"""Testes unitarios do AnalisarAderenciaUseCase (com fakes: sem rede e sem banco)."""

import pytest

from application.use_cases.analisar_aderencia_vaga import (
    AnalisarAderenciaUseCase,
    VagaNaoEncontradaError,
)
from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga


class RepositorioFake:
    """Repositorio falso em memoria."""

    def __init__(self, vagas):
        self._vagas = {vaga.url: vaga for vaga in vagas}

    def salvar(self, vaga):
        self._vagas[vaga.url] = vaga

    def buscar_por_url(self, url):
        return self._vagas.get(url)


class AnalisadorFake:
    """Analisador de IA falso que registra as descricoes recebidas."""

    def __init__(self, palavras_chave):
        self._palavras_chave = list(palavras_chave)
        self.descricoes_recebidas = []

    def extrair_palavras_chave(self, descricao_vaga):
        self.descricoes_recebidas.append(descricao_vaga)
        return list(self._palavras_chave)


def _criar_vaga(url: str, descricao: str) -> Vaga:
    return Vaga(
        titulo="Dev Python",
        empresa="Acme",
        localizacao="Remoto",
        formato=FormatoTrabalho.REMOTO,
        descricao=descricao,
        url=url,
        status=StatusVaga.ATIVA,
    )


def test_deve_buscar_vaga_e_extrair_palavras_chave_com_ia():
    vaga = _criar_vaga("https://acme.gupy.io/job/1", "Vaga com Python, FastAPI e Docker.")
    repositorio = RepositorioFake([vaga])
    analisador = AnalisadorFake(["Python", "FastAPI", "Docker"])

    use_case = AnalisarAderenciaUseCase(repositorio=repositorio, analisador=analisador)

    resultado = use_case.executar("https://acme.gupy.io/job/1")

    assert resultado == ["Python", "FastAPI", "Docker"]
    assert analisador.descricoes_recebidas == ["Vaga com Python, FastAPI e Docker."]


def test_deve_lancar_erro_quando_vaga_nao_encontrada():
    repositorio = RepositorioFake([])
    analisador = AnalisadorFake(["Python"])

    use_case = AnalisarAderenciaUseCase(repositorio=repositorio, analisador=analisador)

    with pytest.raises(VagaNaoEncontradaError):
        use_case.executar("https://acme.gupy.io/job/inexistente")

    assert analisador.descricoes_recebidas == []  # a IA nao deve ser acionada