"""Testes unitarios do GupyScraper (formatacao e resiliencia, sem rede)."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga
from infrastructure.scraper.gupy_scraper import GupyScraper


def test_formatar_secao_deve_gerar_marcacao_md_com_titulo_e_conteudo():
    resultado = GupyScraper._formatar_secao("Descrição da vaga", "Voce ira construir APIs.")

    assert resultado == "### Descrição da vaga\nVoce ira construir APIs.\n\n"


def test_formatar_secao_sem_titulo_deve_usar_cabecalho_generico():
    resultado = GupyScraper._formatar_secao("", "Conteudo solto.")

    assert resultado == "### SECAO\nConteudo solto.\n\n"


def test_extrair_detalhes_vaga_deve_retornar_vazio_para_url_vazia():
    scraper = GupyScraper()

    assert scraper.extrair_detalhes_vaga("") == ""


def test_extrair_detalhes_vaga_deve_retornar_vazio_quando_navegacao_falha(monkeypatch):
    scraper = GupyScraper()

    def _boom():
        raise RuntimeError("browser quebrado")

    monkeypatch.setattr(scraper, "_garantir_page", _boom)

    assert scraper.extrair_detalhes_vaga("https://empresa.gupy.io/job/x") == ""


def test_dentro_do_prazo_deve_aceitar_vaga_publicada_ha_poucos_dias():
    agora = datetime(2026, 9, 8, 12, 0, 0)

    assert GupyScraper._dentro_do_prazo(datetime(2026, 9, 1), agora=agora) is True


def test_dentro_do_prazo_deve_rejeitar_vaga_com_mais_de_30_dias():
    agora = datetime(2026, 9, 8, 12, 0, 0)

    assert GupyScraper._dentro_do_prazo(datetime(2026, 8, 8), agora=agora) is False


def test_dentro_do_prazo_deve_aceitar_vaga_sem_data_detectada():
    assert GupyScraper._dentro_do_prazo(None, agora=datetime(2026, 9, 8)) is True


def test_extrair_vagas_deve_descartar_vagas_publicadas_ha_mais_de_30_dias(monkeypatch):
    agora = datetime.now()
    vaga_recente = Vaga(
        titulo="Vaga recente",
        empresa="Acme",
        localizacao="Remoto",
        formato=FormatoTrabalho.REMOTO,
        descricao="desc",
        url="https://acme.gupy.io/job/recente",
        data_publicacao=agora - timedelta(days=5),
        status=StatusVaga.NOVA,
    )
    vaga_antiga = Vaga(
        titulo="Vaga antiga",
        empresa="Beta",
        localizacao="Remoto",
        formato=FormatoTrabalho.REMOTO,
        descricao="desc",
        url="https://beta.gupy.io/job/antiga",
        data_publicacao=agora - timedelta(days=45),
        status=StatusVaga.NOVA,
    )
    scraper = GupyScraper()
    page_fake = MagicMock()
    page_fake.locator.return_value.all.return_value = [MagicMock(), MagicMock()]
    monkeypatch.setattr(scraper, "_page", page_fake)
    monkeypatch.setattr(scraper, "acessar_pagina", lambda url: None)
    monkeypatch.setattr(
        scraper, "_extrair_vaga_do_card", lambda card: vaga_recente if card is page_fake.locator.return_value.all.return_value[0] else vaga_antiga
    )

    resultado = scraper.extrair_vagas("https://portal.gupy.io/fake-search")

    assert resultado == [vaga_recente]  # vaga antiga filtrada pela regra de 30 dias