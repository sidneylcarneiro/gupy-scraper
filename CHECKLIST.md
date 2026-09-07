# Checklist de Desenvolvimento: Gupy Scraper

Este documento serve como guia de progresso. O agente de IA (Cline) deve consultá-lo e atualizá-lo conforme as etapas forem concluídas.

## 🟢 Fase 0: Planejamento e Escopo

- [X] Definição do Escopo e Regras de Negócio.
- [X] Atualização do `README.md` com arquitetura e nova stack (PostgreSQL, Docker, DDD, TDD).
- [X] Criação deste `CHECKLIST.md`.

## 🟡 Fase 1: Configuração Base (Passo Atual)

- [ ] Inicializar repositório Git.  [github.com/sidneylcarneiro/gupy-scraper](https://github.com/sidneylcarneiro/gupy-scraper) Sincronize com o repositório remoto
- [ ] Criar estrutura de pastas (Clean Architecture: `domain`, `application`, `infrastructure`, `presentation`).
- [ ] Configurar o `docker-compose.yml` para rodar o PostgreSQL.
- [ ] Configurar ambiente virtual Python (ex: `venv`) e arquivos de dependências iniciais (`requirements.txt`).
- [ ] Configurar framework de testes (`pytest`).

## ⚪ Fase 2: Domínio e Casos de Uso (DDD & TDD)

- [ ] Definir Entidades de Domínio (ex: `Vaga`, `Candidatura`).
- [ ] Criar interfaces (Ports) para os repositórios.
- [ ] Escrever os primeiros testes (TDD) para os Casos de Uso (ex: `SalvarVagaUseCase`).

## ⚪ Fase 3: Infraestrutura (Scraping e Banco de Dados)

- [ ] Implementar os Adaptadores de Banco de Dados (SQLAlchemy com PostgreSQL).
- [ ] Implementar o motor de Scraping isolado na camada de infraestrutura.
- [ ] Criar testes de integração para o Scraper e o Banco.

## ⚪ Fase 4: Inteligência Artificial

- [ ] Integrar APIs de IA na camada de infraestrutura.
- [ ] Desenvolver os casos de uso de análise de perfil e mock interview.

## ⚪ Fase 5: Interface (FastAPI e HTMX)

- [ ] Criar rotas FastAPI (Presentation layer).
- [ ] Desenvolver templates e dashboard Kanban (Jinja2 + HTMX).

## ⚪ Fase 6: CI/CD e Finalização

- [ ] Configurar GitHub Actions (Lint, Testes automatizados).
- [ ] Revisão final de Clean Code e documentação do código.
