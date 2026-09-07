"""Testes de integracao do PostgresBuscaRepository contra o PostgreSQL real (Docker)."""

import pytest

from domain.entities.busca import Busca
from infrastructure.database.database import Base
from infrastructure.database.models import BuscaModel  # noqa: F401 (registra as tabelas no Base)
from infrastructure.database.postgres_busca_repository import (
    ApelidoJaExisteError,
    PostgresBuscaRepository,
)
from tests.integration.test_postgres_repository import SessaoTeste, engine_teste


@pytest.fixture
def repositorio():
    """Cria o schema no banco de TESTES antes de cada teste e o remove ao final."""
    Base.metadata.create_all(bind=engine_teste)
    yield PostgresBuscaRepository(session_factory=SessaoTeste)
    Base.metadata.drop_all(bind=engine_teste)
    engine_teste.dispose()


def test_deve_salvar_e_listar_buscas_ordenadas_por_apelido(repositorio):
    repositorio.salvar(Busca(apelido="Python Remoto", url="https://portal.gupy.io/job-search/term=python"))
    repositorio.salvar(Busca(apelido="Dados SP", url="https://portal.gupy.io/job-search/term=dados"))

    buscas = repositorio.listar()

    assert [busca.apelido for busca in buscas] == ["Dados SP", "Python Remoto"]
    assert buscas[1].id is not None


def test_deve_rejeitar_apelido_duplicado(repositorio):
    repositorio.salvar(Busca(apelido="Unica", url="https://portal.gupy.io/job-search/term=x"))

    with pytest.raises(ApelidoJaExisteError):
        repositorio.salvar(Busca(apelido="Unica", url="https://portal.gupy.io/job-search/term=y"))


def test_deve_buscar_por_id_e_remover(repositorio):
    busca = repositorio.salvar(Busca(apelido="Temporaria", url="https://portal.gupy.io/job-search/term=temp"))

    encontrada = repositorio.buscar_por_id(busca.id)
    assert encontrada is not None
    assert encontrada.apelido == "Temporaria"

    repositorio.remover(busca.id)
    assert repositorio.buscar_por_id(busca.id) is None