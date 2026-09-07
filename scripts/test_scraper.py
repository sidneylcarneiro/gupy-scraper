"""Script manual de validacao do scraper (nao faz parte da suite pytest).

Uso, a partir da raiz do projeto:
    PYTHONPATH=. ./venv/bin/python scripts/test_scraper.py
"""

from infrastructure.scraper.gupy_scraper import GupyScraper


def main() -> None:
    url_busca = input("Cole a URL da busca da Gupy: ").strip()
    scraper = GupyScraper()
    vagas = scraper.extrair_vagas(url_busca)

    print(f"\n=== {len(vagas)} vagas extraidas da Gupy ===\n")
    for vaga in vagas:
        data = vaga.data_publicacao.strftime("%d/%m/%Y") if vaga.data_publicacao else "-"
        print(f"- [{vaga.empresa}] {vaga.titulo}")
        print(f"  Local: {vaga.localizacao} | Publicada: {data} | Status: {vaga.status.value}")
        print(f"  URL: {vaga.url}\n")


if __name__ == "__main__":
    main()