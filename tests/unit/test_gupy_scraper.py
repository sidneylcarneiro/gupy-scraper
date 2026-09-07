"""Testes unitarios do GupyScraper (formatacao e resiliencia, sem rede)."""

import pytest

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