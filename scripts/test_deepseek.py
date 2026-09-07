"""Validacao manual da integracao com o DeepSeek (nao faz parte da suite pytest).

Requisitos antes de rodar:
    1. LLM_API_KEY configurada no arquivo .env;
    2. Pipeline de scraping executado (scripts/main.py) para haver vagas no banco.

Uso, a partir da raiz do projeto:
    PYTHONPATH=. ./venv/bin/python scripts/test_deepseek.py
"""

from application.use_cases.analisar_aderencia_vaga import AnalisarAderenciaUseCase
from infrastructure.database.database import Base, SessionLocal, engine
from infrastructure.database.models import VagaModel  # registra a tabela no Base.metadata
from infrastructure.database.postgres_vaga_repository import PostgresVagaRepository
from infrastructure.external_services.llm_analisador import LLMAnalisador


def _primeira_vaga_do_banco() -> VagaModel:
    """Retorna a vaga de menor id (primeira inserida) ou None se a tabela estiver vazia."""
    session = SessionLocal()
    try:
        return session.query(VagaModel).order_by(VagaModel.id).first()
    finally:
        session.close()


def main() -> None:
    """Busca a primeira vaga do PostgreSQL e analisa a descricao com o DeepSeek."""
    Base.metadata.create_all(bind=engine)

    modelo = _primeira_vaga_do_banco()
    if modelo is None:
        print("Nenhuma vaga no banco. Execute scripts/main.py antes para popular a tabela 'vagas'.")
        return

    repositorio = PostgresVagaRepository(SessionLocal)
    analisador = LLMAnalisador()
    use_case = AnalisarAderenciaUseCase(repositorio=repositorio, analisador=analisador)

    palavras_chave = use_case.executar(modelo.url)

    print(f"\nVaga analisada: {modelo.titulo}")
    print(f"URL: {modelo.url}")
    print(f"Palavras-chave extraidas pela IA ({analisador.modelo}): {palavras_chave}\n")


if __name__ == "__main__":
    main()