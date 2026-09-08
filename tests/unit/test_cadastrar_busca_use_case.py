"""Testes unitarios do CadastrarBuscaUseCase e AtualizarBuscaUseCase (fakes)."""

import pytest

from application.use_cases.atualizar_busca import AtualizarBuscaUseCase, BuscaNaoEncontradaError
from application.use_cases.cadastrar_busca import (
    ApelidoInvalidoError,
    CadastrarBuscaUseCase,
    URLInvalidaError,
)


class RepositorioBuscaFake:
    """Repositorio falso que guarda as buscas salvas."""

    def __init__(self):
        self.salvas = {}
        self._proximo_id = 1

    def salvar(self, busca):
        busca.id = self._proximo_id
        self._proximo_id += 1
        self.salvas[busca.id] = busca
        return busca

    def listar(self):
        return list(self.salvas.values())

    def buscar_por_id(self, id_busca):
        return self.salvas.get(id_busca)

    def remover(self, id_busca):
        self.salvas.pop(id_busca, None)

    def atualizar(self, id_busca, apelido, url):
        busca = self.salvas.get(id_busca)
        if busca is None:
            return None
        busca.apelido = apelido
        busca.url = url
        return busca


def test_deve_salvar_busca_com_apelido_e_url():
    repositorio = RepositorioBuscaFake()
    use_case = CadastrarBuscaUseCase(repositorio)

    busca = use_case.executar(
        apelido="Python Remoto",
        url="https://portal.gupy.io/job-search/term=python&workplaceTypes[]=remote",
    )

    assert busca.apelido == "Python Remoto"
    assert busca.url == "https://portal.gupy.io/job-search/term=python&workplaceTypes[]=remote"
    assert len(repositorio.salvas) == 1


def test_deve_normalizar_apelido_com_espacos_extras():
    use_case = CadastrarBuscaUseCase(RepositorioBuscaFake())

    busca = use_case.executar(apelido="  Dados SP  ", url="https://portal.gupy.io/job-search/term=dados")

    assert busca.apelido == "Dados SP"


def test_deve_rejeitar_apelido_vazio():
    use_case = CadastrarBuscaUseCase(RepositorioBuscaFake())

    with pytest.raises(ApelidoInvalidoError):
        use_case.executar(apelido="   ", url="https://portal.gupy.io/job-search/term=x")


def test_deve_rejeitar_url_fora_do_gupy():
    use_case = CadastrarBuscaUseCase(RepositorioBuscaFake())

    with pytest.raises(URLInvalidaError):
        use_case.executar(apelido="LinkedIn", url="https://linkedin.com/jobs")


def test_deve_editar_busca_existente():
    repositorio = RepositorioBuscaFake()
    busca = repositorio.salvar(type("B", (), {"apelido": "Viejo", "url": "https://portal.gupy.io/job-search/term=v", "id": None})())
    use_case = AtualizarBuscaUseCase(repositorio)

    atualizada = use_case.executar(
        id_busca=busca.id, apelido="Python Remoto", url="https://portal.gupy.io/job-search/term=python"
    )

    assert atualizada.apelido == "Python Remoto"
    assert atualizada.url == "https://portal.gupy.io/job-search/term=python"


def test_deve_levantar_erro_para_busca_inexistente():
    use_case = AtualizarBuscaUseCase(RepositorioBuscaFake())

    with pytest.raises(BuscaNaoEncontradaError):
        use_case.executar(999, apelido="X", url="https://portal.gupy.io/job-search/term=x")