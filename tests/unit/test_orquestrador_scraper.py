"""Testes unitarios do OrquestradorScraper (com fakes: sem rede e sem banco)."""

from domain.entities.vaga import FormatoTrabalho, StatusVaga, Vaga

from application.services.orquestrador_scraper import OrquestradorScraper
from application.use_cases.salvar_vaga import SalvarVagaUseCase


class ExtratorFake:
    """Extrator em memoria que simula a listagem e os detalhes das vagas."""

    def __init__(self, vagas, detalhes_por_url):
        self._vagas = list(vagas)
        self._detalhes_por_url = dict(detalhes_por_url)
        self.urls_busca_recebidas = []
        self.urls_consultadas = []
        self.fechado = False

    def extrair_vagas(self, url_busca: str):
        self.urls_busca_recebidas.append(url_busca)
        return list(self._vagas)

    def extrair_detalhes_vaga(self, url):
        self.urls_consultadas.append(url)
        return self._detalhes_por_url.get(url, "")

    def fechar(self):
        self.fechado = True


class RepositorioEmMemoria:
    """Repositorio falso que guarda as vagas salvas."""

    def __init__(self):
        self.vagas_salvas = []

    def salvar(self, vaga):
        self.vagas_salvas.append(vaga)

    def buscar_por_url(self, url):
        for vaga in self.vagas_salvas:
            if vaga.url == url:
                return vaga
        return None


def _criar_vaga(url: str, titulo: str = "Dev Python") -> Vaga:
    return Vaga(
        titulo=titulo,
        empresa="Acme",
        localizacao="Remoto",
        formato=FormatoTrabalho.REMOTO,
        descricao="",
        url=url,
        status=StatusVaga.ATIVA,
    )


URL_BUSCA_FALSA = "https://portal.gupy.io/fake-search"


def test_deve_enriquecer_descricao_e_salvar_todas_as_vagas():
    vaga1 = _criar_vaga("https://acme.gupy.io/job/1")
    vaga2 = _criar_vaga("https://acme.gupy.io/job/2", titulo="Dev Senior")
    detalhes = {
        "https://acme.gupy.io/job/1": "Descricao profunda da vaga 1",
        "https://acme.gupy.io/job/2": "Descricao profunda da vaga 2",
    }
    extrator = ExtratorFake([vaga1, vaga2], detalhes)
    repositorio = RepositorioEmMemoria()

    orquestrador = OrquestradorScraper(
        scraper=extrator,
        salvar_vaga_use_case=SalvarVagaUseCase(repositorio),
    )

    resultado = orquestrador.executar(URL_BUSCA_FALSA)

    assert extrator.urls_busca_recebidas == [URL_BUSCA_FALSA]  # url de busca repassada ao scraper
    assert len(resultado) == 2
    assert resultado[0].descricao == "Descricao profunda da vaga 1"
    assert resultado[1].descricao == "Descricao profunda da vaga 2"
    assert extrator.urls_consultadas == [
        "https://acme.gupy.io/job/1",
        "https://acme.gupy.io/job/2",
    ]
    assert len(repositorio.vagas_salvas) == 2
    assert repositorio.vagas_salvas[0].descricao == "Descricao profunda da vaga 1"
    assert extrator.fechado is True  # browser fechado ao final da orquestracao


def test_deve_salvar_vaga_com_descricao_vazia_quando_detalhe_nao_disponivel():
    vaga = _criar_vaga("https://acme.gupy.io/job/3")
    extrator = ExtratorFake([vaga], detalhes_por_url={})
    repositorio = RepositorioEmMemoria()

    orquestrador = OrquestradorScraper(
        scraper=extrator,
        salvar_vaga_use_case=SalvarVagaUseCase(repositorio),
    )

    resultado = orquestrador.executar(URL_BUSCA_FALSA)

    assert len(resultado) == 1
    assert resultado[0].descricao == ""
    assert repositorio.vagas_salvas[0].url == "https://acme.gupy.io/job/3"