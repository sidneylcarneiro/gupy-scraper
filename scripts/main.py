"""Ponto de entrada CLI do Gupy Scraper (Composition Root).

Executa o fluxo completo de uma URL de busca informada por argumento:
    PYTHONPATH=. ./venv/bin/python scripts/main.py "<url_busca_da_gupy>"

Preferencialmente use o painel web (python -m presentation.app), onde as
buscas sao cadastradas com apelido e executadas por clique.
"""

import sys

from application.services.orquestrador_scraper import OrquestradorScraper
from application.use_cases.salvar_vaga import SalvarVagaUseCase
from infrastructure.database.database import Base, SessionLocal, engine
from infrastructure.database.models import VagaModel  # registra a tabela no Base.metadata
from infrastructure.database.postgres_vaga_repository import PostgresVagaRepository
from infrastructure.scraper.gupy_scraper import GupyScraper


def main() -> None:
    """Executa o pipeline completo de extracao e persistencia de vagas."""
    if len(sys.argv) < 2:
        print("Informe a URL de busca da Gupy como argumento.")
        print('Exemplo: PYTHONPATH=. ./venv/bin/python scripts/main.py "https://portal.gupy.io/job-search/term=python"')
        print("Dica: use o painel web (python -m presentation.app) para cadastrar buscas com apelido.")
        return

    url_busca = sys.argv[1].strip()
    Base.metadata.create_all(bind=engine)

    repositorio = PostgresVagaRepository(SessionLocal)
    salvar_vaga_use_case = SalvarVagaUseCase(repositorio)
    scraper = GupyScraper()
    orquestrador = OrquestradorScraper(
        scraper=scraper,
        salvar_vaga_use_case=salvar_vaga_use_case,
    )

    vagas = orquestrador.executar(url_busca)

    print(f"\n=== {len(vagas)} vagas salvas no PostgreSQL ===\n")
    for vaga in vagas:
        descricao = vaga.descricao.strip()
        trecho = descricao[:80] + "..." if len(descricao) > 80 else (descricao or "(sem descricao)")
        print(f"- [{vaga.empresa}] {vaga.titulo}")
        print(f"  URL: {vaga.url}")
        print(f"  Descricao: {trecho}\n")


if __name__ == "__main__":
    main()