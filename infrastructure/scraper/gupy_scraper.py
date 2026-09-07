"""Scraper da Gupy usando Playwright (camada de infraestrutura).

Os seletores abaixo foram validados contra o HTML real da pagina de busca
da Gupy. Nao invente seletores novos sem antes validar o HTML atual.
"""

import re
from datetime import datetime
from typing import Optional

from playwright.sync_api import Locator, Page, sync_playwright

from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga


class GupyScraper:
    """Responsavel por acessar a pagina de busca da Gupy e extrair as vagas."""

    URL_BUSCA = (
        "https://portal.gupy.io/job-search/term=python&jobTypes[]="
        "vacancy_type_effective,vacancy_type_talent_pool,vacancy_type_volunteer"
        "&workplaceTypes[]=remote"
    )

    SELETOR_LISTA_VAGAS = 'ul[class*="eco-me1nqn"]'
    SELETOR_CARD_VAGA = 'ul[class*="eco-me1nqn"] > li'
    SELETOR_LINK = 'a[target="_blank"]'
    SELETOR_TITULO = "h3"
    SELETOR_EMPRESA = "div > p"
    SELETOR_LOCALIZACAO = 'span[data-testid="job-location"]'
    SELETOR_FOOTER = 'span[data-testid="listing-card-footer"] p'

    def acessar_pagina(self, page: Page) -> None:
        """Navega ate a URL de busca e aguarda a lista de vagas carregar."""
        page.goto(self.URL_BUSCA)
        page.wait_for_selector(self.SELETOR_LISTA_VAGAS, timeout=15000)

    def extrair_vagas(self) -> list[Vaga]:
        """Abre o navegador headless, acessa a busca e extrai as vagas listadas."""
        vagas_extraidas: list[Vaga] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            self.acessar_pagina(page)

            for card in page.locator(self.SELETOR_CARD_VAGA).all():
                vagas_extraidas.append(self._extrair_vaga_do_card(card))

            browser.close()

        return vagas_extraidas

    def extrair_detalhes_vaga(self, url: str) -> str:
        """Acessa a pagina individual da vaga e extrai a descricao completa.

        ATENCAO: esqueleto propositadamente vazio. Implementar somente quando
        o HTML da pagina de detalhes for fornecido (nao inventar seletores).
        """
        return ""

    def _extrair_vaga_do_card(self, card: Locator) -> Vaga:
        """Extrai os dados de um unico card (<li>) da listagem."""
        link = card.locator(self.SELETOR_LINK).first
        url = link.get_attribute("href") if link.count() > 0 else ""

        titulo_locator = card.locator(self.SELETOR_TITULO)
        titulo = titulo_locator.inner_text(timeout=2000) if titulo_locator.count() > 0 else "Sem titulo"

        empresa_locator = card.locator(self.SELETOR_EMPRESA).first
        empresa = empresa_locator.inner_text(timeout=2000) if empresa_locator.count() > 0 else "Confidencial"

        localizacao_locator = card.locator(self.SELETOR_LOCALIZACAO)
        localizacao = (
            localizacao_locator.inner_text(timeout=2000)
            if localizacao_locator.count() > 0
            else "Nao informado"
        )

        footer_locator = card.locator(self.SELETOR_FOOTER)
        footer_texto = footer_locator.inner_text(timeout=2000) if footer_locator.count() > 0 else ""

        return Vaga(
            titulo=titulo,
            empresa=empresa,
            localizacao=localizacao,
            formato=FormatoTrabalho.REMOTO,
            descricao="",  # descricao detalhada sera extraida da pagina individual da vaga
            url=url or "",
            data_publicacao=self._extrair_data_publicacao(footer_texto),
            status=StatusVaga.ATIVA,
        )

    @staticmethod
    def _extrair_data_publicacao(footer_texto: str) -> Optional[datetime]:
        """Extrai a data de publicacao de textos como 'Publicada em: 20/08/2026'."""
        match = re.search(r"\d{2}/\d{2}/\d{4}", footer_texto)
        if match is None:
            return None
        try:
            return datetime.strptime(match.group(), "%d/%m/%Y")
        except ValueError:
            return None