# Checklist de Desenvolvimento: Gupy Scraper

Este documento serve como guia de progresso. O agente de IA (Cline) deve consultá-lo e atualizá-lo conforme as etapas forem concluídas.

## 🟢 Fase 0: Planejamento e Escopo

- [X] Definição do Escopo e Regras de Negócio.
- [X] Atualização do `README.md` com arquitetura e nova stack (PostgreSQL, Docker, DDD, TDD).
- [X] Criação deste `CHECKLIST.md`.

## ✅ Fase 1: Configuração Base (Concluída)

- [X] Inicializar repositório Git.  [github.com/sidneylcarneiro/gupy-scraper](https://github.com/sidneylcarneiro/gupy-scraper) Sincronize com o repositório remoto
- [X] Criar estrutura de pastas (Clean Architecture: `domain`, `application`, `infrastructure`, `presentation`).
- [X] Configurar o `docker-compose.yml` para rodar o PostgreSQL.
- [X] Configurar ambiente virtual Python (ex: `venv`) e arquivos de dependências iniciais (`requirements.txt`).
- [X] Configurar framework de testes (`pytest`).

> **Nota da Fase 1:**
> - Repositório Git inicializado com commit **`0d63c5a`** (branch `main`). O repositório **remoto** (`github.com/sidneylcarneiro/gupy-scraper`) ainda **não foi adicionado/sincronizado** por exigir autenticação. Pendência: executar `git remote add origin <url>` e `git push -u origin main`.
> - PostgreSQL validado com sucesso: container `gupy_scraper_postgres` **healthy** em `0.0.0.0:5434→5432` (porta ajustada de 5432 para 5434 devido a colisão com PostgreSQL local do host e outro container `agendamento_db`).
> - `pytest` configurado e testado com sucesso (1 teste de smoke aprovado).

## ✅ Fase 2: Domínio e Casos de Uso (DDD & TDD) (Concluída)

- [X] Definir Entidades de Domínio (ex: `Vaga`, `Candidatura`).
- [X] Criar interfaces (Ports) para os repositórios.
- [X] Escrever os primeiros testes (TDD) para os Casos de Uso (ex: `SalvarVagaUseCase`).

> **Nota da Fase 2:**
> - Entidade `Vaga` criada em `domain/entities/vaga.py` (dataclass pura, sem dependência de framework) com os campos `titulo`, `empresa`, `localizacao`, `formato`, `descricao`, `url`, `id`, `data_publicacao`, `status`, além dos enums `FormatoTrabalho` e `StatusVaga` e a propriedade `slug`.
> - Port `IVagaRepository` (ABC) criado em `domain/repositories/vaga_repository.py` com os métodos `salvar(vaga)` e `buscar_por_url(url)` — apenas contrato, sem infraestrutura.
> - TDD aplicado na ordem correta: teste criado primeiro em `tests/unit/test_salvar_vaga_use_case.py` com repositório Mock em memória (estado RED confirmado com `ModuleNotFoundError`), depois implementação mínima de `SalvarVagaUseCase` em `application/use_cases/salvar_vaga.py` (estado GREEN: 2 passed).

## 🟡 Fase 3: Infraestrutura (Scraping e Banco de Dados) (Em andamento)

- [X] Implementar os Adaptadores de Banco de Dados (SQLAlchemy com PostgreSQL).
- [ ] Implementar o motor de Scraping isolado na camada de infraestrutura. *(Esqueleto criado: `GupyScraper` com `URL_BUSCA`, `acessar_pagina()` e `extrair_vagas()` vazios — aguardando o HTML real da Gupy para definir os seletores.)*
- [ ] Criar testes de integração para o Scraper e o Banco. *(Banco: ✅ `tests/integration/test_postgres_repository.py` — 2 testes passando contra o PostgreSQL real. Scraper: pendente.)*

> **Nota da Fase 3 (progresso parcial):**
> - `infrastructure/database/database.py`: engine + `SessionLocal` + `Base` lendo `DATABASE_URL` do `.env` (PostgreSQL Docker na porta **5434**, `pool_pre_ping=True`).
> - `infrastructure/database/models.py`: modelo ORM `VagaModel` mapeado para a tabela **`vagas`** (tipagens modernas `Mapped`/`mapped_column` do SQLAlchemy 2.0; `url` com `unique=True`; enums com `native_enum=False`).
> - `infrastructure/database/postgres_vaga_repository.py`: adaptador `PostgresVagaRepository` implementando o port `IVagaRepository` (conversão entidade ↔ modelo, commit/rollback/close por operação).
> - `requirements.txt`: adicionados `SQLAlchemy==2.0.*` e `python-dotenv==1.*` (instalados no venv).
> - TDD respeitado: teste de integração criado primeiro (RED com `ModuleNotFoundError`), depois implementação (GREEN: 2 passed em 3.64s). Suíte completa: **4 passed**.

## ⚪ Fase 4: Inteligência Artificial

- [ ] Integrar APIs de IA na camada de infraestrutura.
- [ ] Desenvolver os casos de uso de análise de perfil e mock interview.

## ⚪ Fase 5: Interface (FastAPI e HTMX)

- [ ] Criar rotas FastAPI (Presentation layer).
- [ ] Desenvolver templates e dashboard Kanban (Jinja2 + HTMX).

## ⚪ Fase 6: CI/CD e Finalização

- [ ] Configurar GitHub Actions (Lint, Testes automatizados).
- [ ] Revisão final de Clean Code e documentação do código.
