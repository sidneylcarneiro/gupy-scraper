"""Testes de integracao do PostgresVagaRepository contra o PostgreSQL real (Docker).

Usam um banco DEDICADO a testes (gupy_scraper_test), derivado da DATABASE_URL,
para nao apagar os dados do banco de desenvolvimento (gupy_scraper) ao rodar
a suite pytest.
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga
from infrastructure.database.database import Base
from infrastructure.database.models import VagaModel  # noqa: F401 (registra as tabelas no Base)
from infrastructure.database.postgres_vaga_repository import PostgresVagaRepository

URL_BASE = os.getenv("DATABASE_URL", "postgresql://gupy:gupy@localhost:5434/gupy_scraper")
TEST_DATABASE_URL = URL_BASE.rsplit("/", 1)[0] + "/gupy_scraper_test"

engine_teste = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
SessaoTeste = sessionmaker(
    bind=engine_teste, autoflush=False, autocommit=False, expire_on_commit=False
)


@pytest.fixture
def repositorio():
    """Cria o schema no banco de TESTES antes de cada teste e o remove ao final."""
    Base.metadata.create_all(bind=engine_teste)
    yield PostgresVagaRepository(session_factory=SessaoTeste)
    Base.metadata.drop_all(bind=engine_teste)
    engine_teste.dispose()


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


def _contar_vagas() -> int:
    session = SessaoTeste()
    try:
        return session.query(VagaModel).count()
    finally:
        session.close()


def test_nao_deve_duplicar_vaga_com_mesma_url(repositorio, vaga_exemplo):
    repositorio.salvar(vaga_exemplo)
    vaga_atualizada = Vaga(
        titulo="Titulo atualizado",
        empresa=vaga_exemplo.empresa,
        localizacao=vaga_exemplo.localizacao,
        formato=vaga_exemplo.formato,
        descricao="Descricao nova",
        url=vaga_exemplo.url,
        data_publicacao=vaga_exemplo.data_publicacao,
        status=vaga_exemplo.status,
    )

    repositorio.salvar(vaga_atualizada)  # nao deve lancar IntegrityError

    assert _contar_vagas() == 1
    vaga_no_banco = repositorio.buscar_por_url(vaga_exemplo.url)
    assert vaga_no_banco.titulo == "Titulo atualizado"
    assert vaga_no_banco.descricao == "Descricao nova"


def test_deve_listar_todas_as_vagas(repositorio, vaga_exemplo):
    repositorio.salvar(vaga_exemplo)
    repositorio.salvar(
        Vaga(
            titulo="Outra vaga",
            empresa="Beta",
            localizacao="Sao Paulo",
            formato=FormatoTrabalho.HIBRIDO,
            descricao="desc",
            url="https://beta.gupy.io/job/outra",
            status=StatusVaga.ATIVA,
        )
    )

    vagas = repositorio.listar_todas()

    assert len(vagas) == 2
    assert {vaga.empresa for vaga in vagas} == {"Gupy", "Beta"}


def test_deve_atualizar_status_da_vaga_pelo_id(repositorio, vaga_exemplo):
    repositorio.salvar(vaga_exemplo)
    vaga_salva = repositorio.buscar_por_url(vaga_exemplo.url)

    atualizada = repositorio.atualizar_status(vaga_salva.id, StatusVaga.CANDIDATURA_ENVIADA)

    assert atualizada is not None
    assert atualizada.status == StatusVaga.CANDIDATURA_ENVIADA
    assert repositorio.buscar_por_url(vaga_exemplo.url).status == StatusVaga.CANDIDATURA_ENVIADA


def test_deve_retornar_none_ao_atualizar_status_de_vaga_inexistente(repositorio):
    assert repositorio.atualizar_status(9999, StatusVaga.REJEITADA) is None


def test_salvar_nao_deve_sobrescrever_status_de_vaga_existente(repositorio, vaga_exemplo):
    """O status definido pelo usuario no Kanban deve sobreviver ao re-scraping."""
    repositorio.salvar(vaga_exemplo)
    vaga_salva = repositorio.buscar_por_url(vaga_exemplo.url)
    repositorio.atualizar_status(vaga_salva.id, StatusVaga.CANDIDATURA_ENVIADA)

    vaga_do_scraper = Vaga(
        titulo="Titulo atualizado pelo scraper",
        empresa=vaga_exemplo.empresa,
        localizacao=vaga_exemplo.localizacao,
        formato=vaga_exemplo.formato,
        descricao="Descricao nova do scraper",
        url=vaga_exemplo.url,  # mesma URL: dispara o upsert
        status=StatusVaga.ATIVA,  # scraper sempre traz ATIVA
    )
    repositorio.salvar(vaga_do_scraper)

    vaga_no_banco = repositorio.buscar_por_url(vaga_exemplo.url)
    assert vaga_no_banco.status == StatusVaga.CANDIDATURA_ENVIADA  # preservado!
    assert vaga_no_banco.titulo == "Titulo atualizado pelo scraper"  # demais campos atualizados