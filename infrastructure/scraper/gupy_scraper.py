"""Scraper da Gupy usando Playwright (camada de infraestrutura).

Os seletores abaixo foram validados contra o HTML real da Gupy (listagem e
pagina de detalhes). Nao invente seletores novos sem antes validar o HTML.
"""

import re
from datetime import datetime, timedelta
from typing import Optional

from playwright.sync_api import Locator, Page, sync_playwright

from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga


class GupyScraper:
    """Extrai vagas da listagem e os detalhes de cada pagina individual.

    Gerencia uma unica instancia de browser/aba reutilizada entre chamadas
    (otimizacao): abre sob demanda na primeira extracao e libera em fechar().
    """

    SELETOR_LISTA_VAGAS = 'ul[class*="eco-me1nqn"]'
    SELETOR_CARD_VAGA = 'ul[class*="eco-me1nqn"] > li'
    SELETOR_LINK = 'a[target="_blank"]'
    SELETOR_TITULO = "h3"
    SELETOR_EMPRESA = "div > p"
    SELETOR_LOCALIZACAO = 'span[data-testid="job-location"]'
    SELETOR_FOOTER = 'span[data-testid="listing-card-footer"] p'

    SELETOR_SECAO_DETALHE = 'div[data-testid="text-section"]'
    SELETOR_TITULO_SECAO = "h2"
    SELETOR_CONTEUDO_SECAO = "div"

    TIMEOUT_SELETOR_MS = 15000
    TIMEOUT_NAVEGACAO_MS = 60000
    TENTATIVAS_NAVEGACAO = 2

    def __init__(self) -> None:
        self._playwright = None
        self._browser = None
        self._page: Optional[Page] = None

    def __enter__(self) -> "GupyScraper":
        self._garantir_page()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.fechar()

    def fechar(self) -> None:
        """Encerra aba, browser e Playwright (seguro se nunca foram abertos)."""
        if self._browser is not None:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None
        self._page = None

    def _garantir_page(self) -> Page:
        """Abre o browser/aba na primeira utilizacao e reutiliza nas seguintes."""
        if self._page is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=True)
            self._page = self._browser.new_page()
        return self._page

    def _navegar(self, page: Page, url: str) -> None:
        """Navega ate a URL e faz uma nova tentativa em caso de falha transitoria.

        Usa domcontentloaded (a Gupy e uma SPA; esperar o evento load completo
        pode estourar o timeout em redes lentas). O conteudo relevante e
        garantido pelo wait_for_selector de cada fluxo.
        """
        ultimo_erro: Optional[Exception] = None
        for _ in range(self.TENTATIVAS_NAVEGACAO):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=self.TIMEOUT_NAVEGACAO_MS)
                return
            except Exception as erro:
                ultimo_erro = erro
        raise ultimo_erro

    def acessar_pagina(self, url_busca: str) -> None:
        """Navega ate a URL de busca informada e aguarda a lista de vagas carregar."""
        page = self._garantir_page()
        self._navegar(page, url_busca)
        page.wait_for_selector(self.SELETOR_LISTA_VAGAS, timeout=self.TIMEOUT_SELETOR_MS)

    DIAS_LIMITE_VAGA = 30

    def extrair_vagas(self, url_busca: str) -> list[Vaga]:
        """Extrai as vagas da listagem da URL de busca informada.

        Regra de negocio: vagas publicadas ha mais de 30 dias sao ignoradas.
        Vagas sem data de publicacao detectavel sao mantidas.
        """
        self.acessar_pagina(url_busca)
        cards = self._page.locator(self.SELETOR_CARD_VAGA).all()

        vagas_extraidas = []
        for card in cards:
            try:
                vaga = self._extrair_vaga_do_card(card)
                if self._dentro_do_prazo(vaga.data_publicacao):
                    vagas_extraidas.append(vaga)
            except Exception as e:
                # Un card malformado (p.ej. footer sin data que lanza timeout) no
                # debe abortar la extraccion: se registra y se sigue con el resto.
                print(f"Erro ao extrair card: {e}")
                continue
        return vagas_extraidas

    @classmethod
    def _dentro_do_prazo(cls, data_publicacao: Optional[datetime], agora: Optional[datetime] = None) -> bool:
        """Indica se a vaga respeita o limite de DIAS_LIMITE_VAGA dias.

        Vagas sem data detectada (None) sao sempre mantidas.
        """
        if data_publicacao is None:
            return True
        limite = (agora or datetime.now()) - timedelta(days=cls.DIAS_LIMITE_VAGA)
        return data_publicacao >= limite

    def extrair_detalhes_vaga(self, url: str) -> str:
        """Extrai a descricao completa da pagina individual da vaga.

        Percorre as secoes (div[data-testid="text-section"]) e monta uma unica
        string no formato '### Titulo\\nconteudo\\n\\n'. Em qualquer falha
        (timeout, pagina invalida etc.) retorna string vazia para nao quebrar
        o scraper inteiro.
        """
        if not url:
            return ""
        try:
            page = self._garantir_page()
            self._navegar(page, url)
            page.wait_for_selector(self.SELETOR_SECAO_DETALHE, timeout=self.TIMEOUT_SELETOR_MS)
            secoes = page.locator(self.SELETOR_SECAO_DETALHE).all()
            partes = [self._extrair_secao(secao) for secao in secoes]
            return "".join(partes).strip()
        except Exception:
            return ""

    def _extrair_secao(self, secao: Locator) -> str:
        """Extrai o titulo (h2) e o conteudo (ultimo div) de uma secao."""
        titulo_locator = secao.locator(self.SELETOR_TITULO_SECAO)
        titulo = titulo_locator.first.inner_text(timeout=5000) if titulo_locator.count() > 0 else ""

        conteudo_locator = secao.locator(self.SELETOR_CONTEUDO_SECAO)
        conteudo = conteudo_locator.last.inner_text(timeout=5000) if conteudo_locator.count() > 0 else ""

        return self._formatar_secao(titulo, conteudo)

    @staticmethod
    def _formatar_secao(titulo: str, conteudo: str) -> str:
        """Formata uma secao como '### Titulo\\nconteudo\\n\\n'."""
        cabecalho = titulo.strip() or "SECAO"
        return f"### {cabecalho}\n{conteudo.strip()}\n\n"

    def _extrair_vaga_do_card(self, card: Locator) -> Vaga:
        """Extrai os dados de um unico card (<li>) da listagem.

        Usa text_content() (leitura instantanea do DOM, sem esperar animaciones)
        para evitar timeouts desnecesarios.
        """
        link = card.locator(self.SELETOR_LINK).first
        url = link.get_attribute("href") if link.count() > 0 else ""

        titulo_locator = card.locator(self.SELETOR_TITULO)
        titulo = titulo_locator.first.text_content() if titulo_locator.count() > 0 else ""
        titulo = (titulo or "").strip() or "Sem titulo"

        empresa_locator = card.locator(self.SELETOR_EMPRESA).first
        empresa = empresa_locator.text_content() if empresa_locator.count() > 0 else ""
        empresa = (empresa or "").strip() or "Confidencial"

        localizacao_locator = card.locator(self.SELETOR_LOCALIZACAO)
        localizacao = (
            localizacao_locator.first.text_content() if localizacao_locator.count() > 0 else ""
        ).strip() or "Nao informado"

        footer_locator = card.locator(self.SELETOR_FOOTER).first
        footer_texto = footer_locator.text_content() if footer_locator.count() > 0 else ""

        return Vaga(
            titulo=titulo,
            empresa=empresa,
            localizacao=localizacao,
            formato=FormatoTrabalho.REMOTO,
            descricao="",  # preenchida na orquestracao via extrair_detalhes_vaga
            url=url or "",
            data_publicacao=self._extrair_data_publicacao(footer_texto or ""),
            status=StatusVaga.NOVA,  # toda vaga raspada nasce no Inbox (triagem)
        )

    @staticmethod
    def _extrair_data_publicacao(footer_texto: str) -> Optional[datetime]:
        """Extrae a data de publicacao de textos como 'Publicada em: 20/08/2026'.

        Regex robusta con grupo de captura. Retorna None (vaga sin data)
        quando nao encontra, mantendo o card pero deteniendo el scraper.
        """
        if not footer_texto:
            return None
        match = re.search(r"(\d{2}/\d{2}/\d{4})", footer_texto)
        if match is None:
            return None
        try:
            return datetime.strptime(match.group(1), "%d/%m/%Y")
        except ValueError:
            return None
