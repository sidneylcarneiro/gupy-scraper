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
        """Extrai as vagas da listagem, busca os detalhes de cada uma e persiste.

        Para cada vaga da listagem:
        1. Extrai a descricao profunda da pagina individual da vaga;
        2. Atualiza o atributo `descricao` da entidade;
        3. Passa a vaga completa para o SalvarVagaUseCase.
        """
        vagas_processadas: list[Vaga] = []

        for vaga in self._scraper.extrair_vagas():
            descricao = self._scraper.extrair_detalhes_vaga(vaga.url)
            vaga_completa = dataclasses.replace(vaga, descricao=descricao)
            vagas_processadas.append(self._salvar_vaga_use_case.executar(vaga_completa))

        return vagas_processadas