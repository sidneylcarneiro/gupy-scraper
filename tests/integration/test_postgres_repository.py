"""Testes de integracao do PostgresVagaRepository contra o PostgreSQL real (Docker)."""

import pytest

from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga
from infrastructure.database.database import Base, SessionLocal, engine
from infrastructure.database.models import VagaModel  # noqa: F401 (registra as tabelas no Base)
from infrastructure.database.postgres_vaga_repository import PostgresVagaRepository


@pytest.fixture
def repositorio():
    """Cria o schema no banco real antes de cada teste e o remove ao final."""
    Base.metadata.create_all(bind=engine)
    yield PostgresVagaRepository(session_factory=SessionLocal)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def vaga_exemplo():
    return Vaga(
        titulo="Desenvolvedor Python Junior",
        empresa="Gupy",
        localizacao="Remoto",
        formato=FormatoTrabalho.REMOTO,
        descricao="Vaga focada em web scraping com Python.",
        url="https://gupy.com/vagas/teste-integracao-python-junior",
        data_publicacao=None,
        status=StatusVaga.ATIVA,
    )


def test_deve_salvar_e_buscar_vaga_por_url_no_postgres(repositorio, vaga_exemplo):
    repositorio.salvar(vaga_exemplo)

    vaga_encontrada = repositorio.buscar_por_url(vaga_exemplo.url)

    assert vaga_encontrada is not None
    assert vaga_encontrada.titulo == vaga_exemplo.titulo
    assert vaga_encontrada.empresa == vaga_exemplo.empresa
    assert vaga_encontrada.localizacao == vaga_exemplo.localizacao
    assert vaga_encontrada.formato == FormatoTrabalho.REMOTO
    assert vaga_encontrada.status == StatusVaga.ATIVA
    assert vaga_encontrada.id is not None


def test_deve_retornar_none_quando_url_nao_existe(repositorio):
    resultado = repositorio.buscar_por_url("https://gupy.com/vagas/nao-existe")

    assert resultado is None