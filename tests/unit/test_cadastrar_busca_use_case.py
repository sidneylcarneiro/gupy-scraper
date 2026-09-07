"""Testes unitarios do CadastrarBuscaUseCase (com fakes, custo zero)."""

import pytest

from application.use_cases.cadastrar_busca import ApelidoInvalidoError, URLInvalidaError
from application.use_cases.cadastrar_busca import CadastrarBuscaUseCase


class RepositorioBuscaFake:
    """Repositorio falso que guarda as buscas salvas."""

    def __init__(self):
        self.salvas = []

    def salvar(self, busca):
        self.salvas.append(busca)
        return busca

    def listar(self):
        return list(self.salvas)


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