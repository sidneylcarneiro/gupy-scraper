"""Esqueleto do scraper da Gupy (camada de infraestrutura).

ATENCAO: os metodos `acessar_pagina` e `extrair_vagas` estao vazios de proposito.
Os seletores HTML reais serao implementados somente quando o HTML da pagina
for fornecido, evitando qualquer chute de seletores.
"""


class GupyScraper:
    """Responsavel por acessar a pagina de busca da Gupy e extrair as vagas."""

    URL_BUSCA = "https://portal.gupy.io/job-search/term=python&jobTypes[]=vacancy_type_effective,vacancy_type_talent_pool,vacancy_type_volunteer&workplaceTypes[]=remote"

    def acessar_pagina(self) -> None:
        """Acessa a URL de busca na Gupy (a ser implementado)."""
        pass

    def extrair_vagas(self) -> list:
        """Extrai os dados das vagas da pagina carregada (a ser implementado)."""
        return []