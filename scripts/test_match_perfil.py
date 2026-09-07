"""Validacao manual do match perfil x vaga via DeepSeek (nao faz parte da suite pytest).

Requisitos antes de rodar:
    1. LLM_API_KEY configurada no arquivo .env;
    2. Pipeline de scraping executado (scripts/main.py) para haver vagas no banco.

Uso, a partir da raiz do projeto:
    PYTHONPATH=. ./venv/bin/python scripts/test_match_perfil.py
"""

from application.use_cases.analisar_aderencia_vaga import AnalisarAderenciaUseCase
from application.use_cases.analisar_perfil_candidato import AnalisarPerfilCandidatoUseCase
from domain.entities.perfil import PerfilCandidato
from infrastructure.database.database import Base, SessionLocal, engine
from infrastructure.database.models import VagaModel  # registra a tabela no Base.metadata
from infrastructure.database.postgres_vaga_repository import PostgresVagaRepository
from infrastructure.external_services.llm_analisador import LLMAnalisador

candidato = PerfilCandidato(
    nome="Sidney Luiz Carneiro",
    resumo_experiencia="Desenvolvedor focado em ecossistema Python e integração de Inteligência Artificial. Experiência na criação e prototipação de aplicações utilizando modelos Gemini (Flash e Pro) via Google AI Studio, bem como ChatGPT e APIs via OpenRouter. Sólida vivência em infraestrutura e hospedagem em nuvem utilizando Google Cloud Platform (GCP) e Render. Experiência em modelagem e gerenciamento de banco de dados NoSQL com MongoDB Atlas, além de conhecimentos práticos em edição e automação de vídeo digital."
)


def _primeira_vaga_do_banco() -> VagaModel:
    """Retorna a vaga de menor id (primeira inserida) ou None se a tabela estiver vazia."""
    session = SessionLocal()
    try:
        return session.query(VagaModel).order_by(VagaModel.id).first()
    finally:
        session.close()


def main() -> None:
    """Cruza as keywords da primeira vaga do banco com o perfil do candidato."""
    Base.metadata.create_all(bind=engine)

    modelo = _primeira_vaga_do_banco()
    if modelo is None:
        print("Nenhuma vaga no banco. Execute scripts/main.py antes para popular a tabela 'vagas'.")
        return

    repositorio = PostgresVagaRepository(SessionLocal)
    analisador = LLMAnalisador()

    aderencia = AnalisarAderenciaUseCase(repositorio=repositorio, analisador=analisador)
    keywords = aderencia.executar(modelo.url)

    match = AnalisarPerfilCandidatoUseCase(analisador=analisador)
    resultado = match.executar(vaga_keywords=keywords, perfil_candidato=candidato.resumo_experiencia)

    aderentes = resultado.get("aderentes", [])
    faltantes = resultado.get("faltantes", [])

    print(f"\n=== MATCH: {candidato.nome} x '{modelo.titulo}' ({modelo.empresa}) ===")
    print(f"Keywords da vaga ({len(keywords)}): {keywords}\n")

    print(f"✅ Aderentes ({len(aderentes)}):")
    for habilidade in aderentes:
        print(f"   - {habilidade}")

    print(f"\n⚠️ Faltantes ({len(faltantes)}):")
    for habilidade in faltantes:
        print(f"   - {habilidade}")
    print()


if __name__ == "__main__":
    main()