"""Testes unitarios dos casos de uso ListarVagas e AtualizarStatusVaga (fakes)."""

import pytest

from application.use_cases.atualizar_status_vaga import AtualizarStatusVagaUseCase
from application.use_cases.buscar_vaga_por_id import BuscarVagaPorIdUseCase, VagaNaoEncontradaError
from application.use_cases.limpar_kanban import LimparKanbanUseCase
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

    def buscar_por_id(self, id_vaga):
        return self.vagas.get(id_vaga)

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


def test_buscar_vaga_por_id_deve_retornar_vaga_existente():
    repositorio = RepositorioVagaFake([_vaga(3, StatusVaga.NOVA)])
    use_case = BuscarVagaPorIdUseCase(repositorio)

    vaga = use_case.executar(3)

    assert vaga.id == 3
    assert vaga.status == StatusVaga.NOVA


def test_buscar_vaga_por_id_deve_levantar_erro_para_vaga_inexistente():
    use_case = BuscarVagaPorIdUseCase(RepositorioVagaFake([]))

    with pytest.raises(VagaNaoEncontradaError):
        use_case.executar(999)


def test_limpar_kanban_deve_descartar_apenas_vagas_em_processo():
    repositorio = RepositorioVagaFake(
        [
            _vaga(1, StatusVaga.ATIVA),
            _vaga(2, StatusVaga.CANDIDATURA_ENVIADA),
            _vaga(3, StatusVaga.EM_ANDAMENTO),
            _vaga(4, StatusVaga.REJEITADA),
            _vaga(5, StatusVaga.CONTRATADA),
            _vaga(6, StatusVaga.NOVA),
            _vaga(7, StatusVaga.DESCARTADA),
        ]
    )
    use_case = LimparKanbanUseCase(repositorio)

    quantidade = use_case.executar()

    assert quantidade == 5  # NOVA (6) e DESCARTADA (7) nao sao tocadas
    assert repositorio.vagas[6].status == StatusVaga.NOVA
    assert repositorio.vagas[7].status == StatusVaga.DESCARTADA
    for id_vaga in (1, 2, 3, 4, 5):
        assert repositorio.vagas[id_vaga].status == StatusVaga.DESCARTADA


def test_limpar_kanban_vazio_deve_retornar_zero():
    use_case = LimparKanbanUseCase(RepositorioVagaFake([]))

    assert use_case.executar() == 0