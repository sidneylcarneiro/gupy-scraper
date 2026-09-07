"""Ponto de entrada do Gupy Scraper (Composition Root).

Monta as dependencias reais (PostgreSQL, repositorio, caso de uso, scraper e
orquestrador) e executa o fluxo completo: extracao profunda + persistencia.

Uso, a partir da raiz do projeto:
    PYTHONPATH=. ./venv/bin/python scripts/main.py
"""

from application.services.orquestrador_scraper import OrquestradorScraper
from application.use_cases.salvar_vaga import SalvarVagaUseCase
from infrastructure.database.database import Base, SessionLocal, engine
from infrastructure.database.models import VagaModel  # registra a tabela no Base.metadata
from infrastructure.database.postgres_vaga_repository import PostgresVagaRepository
from infrastructure.scraper.gupy_scraper import GupyScraper


def main() -> None:
    """Executa o pipeline completo de extracao e persistencia de vagas."""
    Base.metadata.create_all(bind=engine)

    repositorio = PostgresVagaRepository(SessionLocal)
    salvar_vaga_use_case = SalvarVagaUseCase(repositorio)
    scraper = GupyScraper()
    orquestrador = OrquestradorScraper(
        scraper=scraper,
        salvar_vaga_use_case=salvar_vaga_use_case,
    )

    url_busca = input("Cole a URL da busca da Gupy: ").strip()
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