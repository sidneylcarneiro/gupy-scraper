"""Testes unitarios do caso de uso SalvarVagaUseCase (TDD - Fase 2)."""

from typing import Optional

import pytest

from application.use_cases.salvar_vaga import SalvarVagaUseCase
from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga
from domain.repositories.vaga_repository import IVagaRepository


class RepositorioVagasEmMemoria(IVagaRepository):
    """Repositorio falso (mock) em memoria para exercitar o caso de uso."""

    def __init__(self):
        self.vagas_salvas = []

    def salvar(self, vaga: Vaga) -> None:
        self.vagas_salvas.append(vaga)

    def buscar_por_url(self, url: str) -> Optional[Vaga]:
        for vaga in self.vagas_salvas:
            if vaga.url == url:
                return vaga
        return None

    def listar_todas(self) -> list[Vaga]:
        return list(self.vagas_salvas)

    def buscar_por_id(self, id_vaga: int) -> Optional[Vaga]:
        for vaga in self.vagas_salvas:
            if vaga.id == id_vaga:
                return vaga
        return None

    def atualizar_status(self, id_vaga: int, status: StatusVaga) -> Optional[Vaga]:
        for vaga in self.vagas_salvas:
            if vaga.id == id_vaga:
                vaga.status = status
                return vaga
        return None


@pytest.fixture
def repositorio_mock():
    return RepositorioVagasEmMemoria()


@pytest.fixture
def vaga_exemplo():
    return Vaga(
        titulo="Desenvolvedor Python Junior",
        empresa="Gupy",
        localizacao="Sao Paulo (Remoto)",
        formato=FormatoTrabalho.REMOTO,
        descricao="Vaga para desenvolvedor Python junior focada em web scraping.",
        url="https://gupy.com/vagas/desenvolvedor-python-junior",
    )


def test_deve_salvar_uma_vaga_no_repositorio(repositorio_mock, vaga_exemplo):
    use_case = SalvarVagaUseCase(repositorio=repositorio_mock)

    vaga_salva = use_case.executar(vaga=vaga_exemplo)

    assert vaga_salva == vaga_exemplo
    assert len(repositorio_mock.vagas_salvas) == 1
    assert repositorio_mock.buscar_por_url(vaga_exemplo.url) == vaga_exemplo