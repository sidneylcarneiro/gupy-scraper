"""Testes unitarios dos casos de uso ListarVagas e AtualizarStatusVaga (fakes)."""

import pytest

from application.use_cases.atualizar_status_vaga import (
    AtualizarStatusVagaUseCase,
    VagaNaoEncontradaError,
)
from application.use_cases.listar_vagas import ListarVagasUseCase
from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga


class RepositorioVagaFake:
    """Repositorio falso em memoria (listar_todas e atualizar_status)."""

    def __init__(self, vagas):
        self.vagas = {vaga.id: vaga for vaga in vagas}

    def salvar(self, vaga):
        pass

    def buscar_por_url(self, url):
        return None

    def listar_todas(self):
        return list(self.vagas.values())

    def atualizar_status(self, id_vaga, status):
        vaga = self.vagas.get(id_vaga)
        if vaga is None:
            return None
        vaga.status = status
        return vaga


def _vaga(id_vaga, status=StatusVaga.ATIVA):
    return Vaga(
        titulo=f"Dev {id_vaga}",
        empresa="Acme",
        localizacao="Remoto",
        formato=FormatoTrabalho.REMOTO,
        descricao="desc",
        url=f"https://acme.gupy.io/job/{id_vaga}",
        id=id_vaga,
        status=status,
    )


def test_listar_vagas_deve_retornar_todas_as_vagas_do_repositorio():
    repositorio = RepositorioVagaFake([_vaga(1), _vaga(2, StatusVaga.REJEITADA)])
    use_case = ListarVagasUseCase(repositorio)

    resultado = use_case.executar()

    assert len(resultado) == 2
    assert {vaga.id for vaga in resultado} == {1, 2}


def test_atualizar_status_deve_alterar_status_da_vaga():
    repositorio = RepositorioVagaFake([_vaga(7)])
    use_case = AtualizarStatusVagaUseCase(repositorio)

    vaga_atualizada = use_case.executar(7, StatusVaga.CANDIDATURA_ENVIADA)

    assert vaga_atualizada.status == StatusVaga.CANDIDATURA_ENVIADA
    assert repositorio.vagas[7].status == StatusVaga.CANDIDATURA_ENVIADA


def test_atualizar_status_deve_levantar_erro_para_vaga_inexistente():
    use_case = AtualizarStatusVagaUseCase(RepositorioVagaFake([]))

    with pytest.raises(VagaNaoEncontradaError):
        use_case.executar(999, StatusVaga.CONTRATADA)