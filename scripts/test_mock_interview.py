"""Validacao manual do mock interview via DeepSeek (nao faz parte da suite pytest).

Requisito: LLM_API_KEY configurada no arquivo .env.

Uso, a partir da raiz do projeto:
    PYTHONPATH=. ./venv/bin/python scripts/test_mock_interview.py
"""

from dotenv import load_dotenv

load_dotenv()  # carrega LLM_API_KEY do .env antes de instanciar o analisador

from application.use_cases.gerar_mock_interview import GerarMockInterviewUseCase
from infrastructure.external_services.llm_analisador import LLMAnalisador

TITULO_VAGA = "Pessoa Desenvolvedora Backend Python Especialista I (Venda Direta)"
HABILIDADES_FALTANTES = ["React", "AWS", "Testes automatizados", "Scrum"]


def main() -> None:
    """Gera e imprime 5 perguntas de mock interview via DeepSeek."""
    analisador = LLMAnalisador()
    use_case = GerarMockInterviewUseCase(analisador=analisador)

    perguntas = use_case.executar(
        titulo_vaga=TITULO_VAGA, habilidades_faltantes=HABILIDADES_FALTANTES
    )

    print(f"\n=== MOCK INTERVIEW: {TITULO_VAGA} ===")
    print(f"Foco: {HABILIDADES_FALTANTES}\n")

    if not perguntas:
        print("Nenhuma pergunta gerada (verifique a LLM_API_KEY ou os logs de erro).")
        return

    for indice, pergunta in enumerate(perguntas, start=1):
        print(f"{indice}. {pergunta}")
    print()


if __name__ == "__main__":
    main()