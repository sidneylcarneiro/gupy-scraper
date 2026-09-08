"""Painel web do Gupy Scraper (FastAPI + HTMX, camada de presentation).

O usuario cadastra as URLs de busca da Gupy com um apelido, gerencia a lista
e dispara a extracao de cada busca salva pelo painel.
"""

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from application.services.orquestrador_scraper import OrquestradorScraper
from application.use_cases.atualizar_status_vaga import AtualizarStatusVagaUseCase
from application.use_cases.buscar_vaga_por_id import (
    BuscarVagaPorIdUseCase,
    VagaNaoEncontradaError,
)
from application.use_cases.cadastrar_busca import (
    ApelidoInvalidoError,
    CadastrarBuscaUseCase,
    URLInvalidaError,
)
from application.use_cases.limpar_kanban import LimparKanbanUseCase
from application.use_cases.listar_vagas import ListarVagasUseCase
from application.use_cases.salvar_vaga import SalvarVagaUseCase
from domain.entities.vaga import StatusVaga, Vaga
from domain.repositories.busca_repository import IBuscaRepository
from domain.repositories.vaga_repository import IVagaRepository
from infrastructure.database.database import Base, SessionLocal, engine
from infrastructure.database.models import VagaModel  # registra as tabelas no Base.metadata
from infrastructure.database.postgres_busca_repository import PostgresBuscaRepository
from infrastructure.database.postgres_vaga_repository import PostgresVagaRepository
from infrastructure.scraper.gupy_scraper import GupyScraper

app = FastAPI(title="Gupy Scraper - Painel de Buscas")
templates = Jinja2Templates(directory="presentation/templates")


def get_busca_repository() -> IBuscaRepository:
    """Fornece o repositorio real de buscas (sobrescrito nos testes)."""
    return PostgresBuscaRepository(SessionLocal)


def get_vaga_repository() -> IVagaRepository:
    """Fornece o repositorio real de vagas (sobrescrito nos testes)."""
    return PostgresVagaRepository(SessionLocal)


@app.on_event("startup")
def criar_schema() -> None:
    """Garante o schema atualizado ao subir o painel."""
    Base.metadata.create_all(bind=engine)


def _renderizar_lista(request: Request, repositorio: IBuscaRepository, mensagem: str = ""):
    buscas = repositorio.listar()
    return templates.TemplateResponse(
        request,
        "partials/lista_buscas.html",
        {"buscas": buscas, "mensagem": mensagem},
    )


def get_orquestrador() -> OrquestradorScraper:
    """Fornece o orquestrador real (sobrescrito nos testes com fakes)."""
    return OrquestradorScraper(
        scraper=GupyScraper(),
        salvar_vaga_use_case=SalvarVagaUseCase(PostgresVagaRepository(SessionLocal)),
    )


CABECALHOS_SEM_CACHE = {"Cache-Control": "no-cache, no-store, must-revalidate"}


@app.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    repositorio: IBuscaRepository = Depends(get_busca_repository),
    repositorio_vagas: IVagaRepository = Depends(get_vaga_repository),
):
    """Motor de operacao: dropdown de buscas salvas + resultados da extracao."""
    vagas_novas = [
        vaga for vaga in ListarVagasUseCase(repositorio_vagas).executar()
        if vaga.status == StatusVaga.NOVA
    ]
    return templates.TemplateResponse(
        request,
        "index.html",
        {"buscas": repositorio.listar(), "vagas_novas": vagas_novas},
        headers=CABECALHOS_SEM_CACHE,
    )


@app.post("/buscar", response_class=HTMLResponse)
def buscar(
    request: Request,
    id_busca: int = Form(...),
    repositorio: IBuscaRepository = Depends(get_busca_repository),
    repositorio_vagas: IVagaRepository = Depends(get_vaga_repository),
    orquestrador: OrquestradorScraper = Depends(get_orquestrador),
):
    """Executa a busca selecionada e retorna o fragmento com as vagas NOVA."""
    busca = repositorio.buscar_por_id(id_busca)
    if busca is None:
        return templates.TemplateResponse(
            request,
            "partials/resultados_busca.html",
            {"vagas_novas": [], "mensagem": "Erro: busca nao encontrada."},
        )

    try:
        orquestrador.executar(busca.url)
    except Exception as erro:
        return templates.TemplateResponse(
            request,
            "partials/resultados_busca.html",
            {"vagas_novas": [], "mensagem": f"Erro ao executar a busca: {erro}"},
        )

    vagas_novas = [
        vaga for vaga in ListarVagasUseCase(repositorio_vagas).executar()
        if vaga.status == StatusVaga.NOVA
    ]
    return templates.TemplateResponse(
        request,
        "partials/resultados_busca.html",
        {"vagas_novas": vagas_novas, "mensagem": ""},
    )


@app.post("/buscas", response_class=HTMLResponse)
def cadastrar_busca(
    request: Request,
    apelido: str = Form(""),
    url: str = Form(""),
    repositorio: IBuscaRepository = Depends(get_busca_repository),
):
    """Cadastra uma nova busca (apelido + URL) e devolve a lista atualizada."""
    use_case = CadastrarBuscaUseCase(repositorio)
    try:
        use_case.executar(apelido=apelido, url=url)
        return _renderizar_lista(request, repositorio, mensagem=f"Busca '{apelido.strip()}' cadastrada com sucesso!")
    except (ApelidoInvalidoError, URLInvalidaError) as erro:
        return _renderizar_lista(request, repositorio, mensagem=f"Erro: {erro}")


@app.delete("/buscas/{id_busca}", response_class=HTMLResponse)
def remover_busca(
    request: Request,
    id_busca: int,
    repositorio: IBuscaRepository = Depends(get_busca_repository),
):
    """Remove uma busca salva e devolve a lista atualizada."""
    repositorio.remover(id_busca)
    return _renderizar_lista(request, repositorio, mensagem="Busca removida.")


@app.post("/buscas/{id_busca}/executar", response_class=HTMLResponse)
def executar_busca(
    request: Request,
    id_busca: int,
    repositorio: IBuscaRepository = Depends(get_busca_repository),
    repositorio_vagas: IVagaRepository = Depends(get_vaga_repository),
):
    """Roda o pipeline completo (scraping + detalhes + persistencia) da busca."""
    busca = repositorio.buscar_por_id(id_busca)
    if busca is None:
        return _renderizar_lista(request, repositorio, mensagem="Erro: busca nao encontrada.")

    orquestrador = OrquestradorScraper(
        scraper=GupyScraper(),
        salvar_vaga_use_case=SalvarVagaUseCase(repositorio_vagas),
    )
    try:
        vagas = orquestrador.executar(busca.url)
        return _renderizar_lista(
            request,
            repositorio,
            mensagem=f"Busca '{busca.apelido}' executada: {len(vagas)} vaga(s) salva(s) no PostgreSQL.",
        )
    except Exception as erro:
        return _renderizar_lista(request, repositorio, mensagem=f"Erro ao executar a busca: {erro}")


STATUS_FORA_DO_KANBAN = (StatusVaga.NOVA, StatusVaga.DESCARTADA)


@app.get("/kanban", response_class=HTMLResponse)
def kanban(request: Request, repositorio_vagas: IVagaRepository = Depends(get_vaga_repository)):
    """Dashboard Kanban com as vagas em processo, agrupadas por status.

    Vagas NOVA (aguardando triagem no Inbox) e DESCARTADA nao aparecem aqui.
    """
    vagas = ListarVagasUseCase(repositorio_vagas).executar()
    vagas_em_processo = [vaga for vaga in vagas if vaga.status not in STATUS_FORA_DO_KANBAN]
    vagas_por_status = {status: [] for status in StatusVaga if status not in STATUS_FORA_DO_KANBAN}
    for vaga in vagas_em_processo:
        vagas_por_status[vaga.status].append(vaga)
    return templates.TemplateResponse(
        request,
        "kanban.html",
        {"vagas_por_status": vagas_por_status, "total_vagas": len(vagas_em_processo)},
        headers=CABECALHOS_SEM_CACHE,
    )


@app.get("/vagas/{id_vaga}", response_class=HTMLResponse)
def detalhes_vaga(
    request: Request,
    id_vaga: int,
    repositorio_vagas: IVagaRepository = Depends(get_vaga_repository),
):
    """Pagina dedicada com os detalhes da vaga (e espaco para as analises de IA)."""
    try:
        vaga = BuscarVagaPorIdUseCase(repositorio_vagas).executar(id_vaga)
    except VagaNaoEncontradaError:
        return HTMLResponse("<h1>Vaga nao encontrada</h1>", status_code=404)
    return templates.TemplateResponse(
        request,
        "vaga_detalhes.html",
        {"vaga": vaga},
        headers=CABECALHOS_SEM_CACHE,
    )


@app.post("/kanban/limpar", response_class=HTMLResponse)
def limpar_kanban(repositorio_vagas: IVagaRepository = Depends(get_vaga_repository)):
    """Descarta todas as vagas em processo e pede o refresh do HTMX."""
    quantidade = LimparKanbanUseCase(repositorio_vagas).executar()
    return HTMLResponse(
        f"<div class='mensagem'>{quantidade} vaga(s) descartada(s). Painel limpo!</div>",
        headers={"HX-Refresh": "true"},
    )


@app.get("/configuracoes", response_class=HTMLResponse)
def configuracoes(request: Request, repositorio: IBuscaRepository = Depends(get_busca_repository)):
    """Unico lugar onde se cria ou remove um link de busca (apelido + URL)."""
    return templates.TemplateResponse(
        request,
        "configuracoes.html",
        {"buscas": repositorio.listar(), "mensagem": ""},
        headers=CABECALHOS_SEM_CACHE,
    )


@app.patch("/vagas/{id_vaga}/status", response_class=HTMLResponse)
def atualizar_status_vaga(
    request: Request,
    id_vaga: int,
    status: str = Form(""),
    repositorio_vagas: IVagaRepository = Depends(get_vaga_repository),
):
    """Atualiza o status da vaga (HTMX) e devolve apenas o card atualizado."""
    try:
        novo_status = StatusVaga(status)
    except ValueError:
        return HTMLResponse(f"<div class='mensagem erro'>Status invalido: {status}</div>")

    use_case = AtualizarStatusVagaUseCase(repositorio_vagas)
    vaga = use_case.executar(id_vaga, novo_status)
    return templates.TemplateResponse(
        request,
        "partials/card_vaga.html",
        {"vaga": vaga},
    )


def _card_da_vaga(request: Request, vaga: Vaga):
    return templates.TemplateResponse(request, "partials/card_vaga.html", {"vaga": vaga})