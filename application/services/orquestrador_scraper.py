"""Servico de aplicacao que orquestra a extracao profunda e a persistencia de vagas."""

import dataclasses

from application.interfaces.extrator_vagas_port import IExtratorDeVagas
from application.use_cases.salvar_vaga import SalvarVagaUseCase
from domain.entities.vaga import Vaga


class OrquestradorScraper:
    """Coordena o fluxo completo: listar vagas, enriquecer com detalhes e salvar."""

    def __init__(self, scraper: IExtratorDeVagas, salvar_vaga_use_case: SalvarVagaUseCase):
        self._scraper = scraper
        self._salvar_vaga_use_case = salvar_vaga_use_case

    def executar(self) -> list[Vaga]:
        """Extrai, enriquece e salva as vagas reutilizando um unico browser.

        O browser e aberto na primeira extracao e fechado ao final da
        orquestracao (mesmo em caso de erro), evitando abrir/fechar por URL.
        """
        vagas_processadas: list[Vaga] = []
        try:
            for vaga in self._scraper.extrair_vagas():
                descricao = self._scraper.extrair_detalhes_vaga(vaga.url)
                vaga_completa = dataclasses.replace(vaga, descricao=descricao)
                vagas_processadas.append(self._salvar_vaga_use_case.executar(vaga_completa))
        finally:
            self._scraper.fechar()
        return vagas_processadas