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

## ✅ Fase 3: Infraestrutura (Scraping e Banco de Dados) (Concluída)

- [X] Implementar os Adaptadores de Banco de Dados (SQLAlchemy com PostgreSQL).
- [X] Implementar o motor de Scraping isolado na camada de infraestrutura. *(Implementado com Playwright/Chromium headless; seletores validados no HTML real da Gupy fornecido pelo usuário.)*
- [X] Criar testes de integração para o Scraper e o Banco. *(Banco: `tests/integration/test_postgres_repository.py` — 2 testes contra o PostgreSQL real. Scraper: validado em execução real via `scripts/test_scraper.py` — 12 vagas extraídas.)*

> **Nota da Fase 3:**
> - `infrastructure/database/database.py`: engine + `SessionLocal` + `Base` lendo `DATABASE_URL` do `.env` (PostgreSQL Docker na porta **5434**, `pool_pre_ping=True`).
> - `infrastructure/database/models.py`: modelo ORM `VagaModel` mapeado para a tabela **`vagas`** (tipagens modernas `Mapped`/`mapped_column` do SQLAlchemy 2.0; `url` com `unique=True`; enums com `native_enum=False`).
> - `infrastructure/database/postgres_vaga_repository.py`: adaptador `PostgresVagaRepository` implementando o port `IVagaRepository` (conversão entidade ↔ modelo, commit/rollback/close por operação).
> - `infrastructure/scraper/gupy_scraper.py`: `GupyScraper` com Playwright — `URL_BUSCA` conforme definida, seletores reais extraídos do HTML validado (`ul[class*="eco-me1nqn"] > li`, `a[target="_blank"]`, `h3`, `div > p`, `span[data-testid="job-location"]`, `span[data-testid="listing-card-footer"] p`), parsing de "Publicada em: dd/mm/aaaa" via regex + `strptime`, retornando entidades de domínio `Vaga` (`StatusVaga.ATIVA`, `FormatoTrabalho.REMOTO`). A descrição detalhada fica para a página individual da vaga.
> - `scripts/test_scraper.py`: script manual de validação (fora da suíte pytest). Execução real contra a Gupy: **12 vagas extraídas** (Grupo Boticário, Claro/Hacktown 2026, Grupo SysMap, Montreal, Hitss Brasil, Deliver IT, 3S Checkout, Confitec, Pulsus), com título, empresa, URL e data de publicação corretos.
> - `playwright==1.62.*` adicionado ao `requirements.txt` e instalado no venv; Chromium **151.0.7922.34** instalado em `~/.cache/ms-playwright` (`chromium-1234` e `chromium_headless_shell-1234` + marca `INSTALLATION_COMPLETE`). *Observação: o `cdn.playwright.dev` estava inacessível na rede (timeout/ECONNRESET), então o download foi feito manualmente do CDN oficial do Chrome for Testing (`storage.googleapis.com`) e extraído no layout esperado pelo Playwright.*
> - TDD respeitado: teste de integração do banco criado primeiro (RED → GREEN). Suíte completa: **4 passed** (2 unitários + 2 integração).

### 🔁 Subtarefa: Integração End-to-End e Extração Profunda (pós-Fase 3)

- [X] Criar método `extrair_detalhes_vaga(self, url: str) -> str` em `GupyScraper` *(esqueleto: retorna `""` — seletores da página de detalhes pendentes do HTML real, que não será inventado)*.
- [X] Criar o Application Service `OrquestradorScraper` em `application/services/orquestrador_scraper.py` (recebe o scraper e o `SalvarVagaUseCase` no construtor).
- [X] Lógica de orquestração no `executar()`: lista as vagas → para cada uma chama `extrair_detalhes_vaga(vaga.url)`, atualiza `descricao` (via `dataclasses.replace`, mantendo imutabilidade do fluxo) → salva pelo `SalvarVagaUseCase`.
- [X] Criar o port `IExtratorDeVagas` (Protocol) em `application/interfaces/extrator_vagas_port.py` — a aplicação depende apenas da abstração, não do Playwright (DIP).
- [X] Criar o ponto de entrada `scripts/main.py` (Composition Root): engine/`SessionLocal` → `PostgresVagaRepository` → `SalvarVagaUseCase` → `GupyScraper` → `OrquestradorScraper.executar()` + `create_all` do schema. **Ainda não executado** (extração profunda vazia).
- [X] Testes unitários do orquestrador com fakes (sem rede/banco): `tests/unit/test_orquestrador_scraper.py` — enriquecimento de descrição + salvamento de todas as vagas e fallback com descrição vazia.
- [X] Implementar os seletores reais de `extrair_detalhes_vaga` *(implementado com o HTML validado: `div[data-testid="text-section"]`, título via `h2`, conteúdo via último `div`, saída concatenada como `### Titulo\nconteudo\n\n`; falhas de navegação/timeout tratadas com try/except retornando `""`)*.
- [X] Executar o pipeline end-to-end real (`scripts/main.py`): scraping profundo → PostgreSQL. **✅ Executado com sucesso: 12/12 vagas persistidas, todas com descrição (2.275 a 7.514 caracteres).**

> **Nota da subtarefa:**
> - Orquestrador validado por testes unitários com `ExtratorFake` e repositório em memória (sem tocar em rede ou banco).
> - **Otimização do scraper (conforme solicitado):** `GupyScraper` agora gerencia 1 única instância de browser/aba — abre sob demanda (`_garantir_page`) e reutiliza com `page.goto()`; fechamento garantido pelo orquestrador no `finally` (e suporte a context manager `with`). Port `IExtratorDeVagas` ganhou o método `fechar()`.
> - **Navegação resiliente:** `goto` com `wait_until="domcontentloaded"`, timeout de 60s e 1 retry (a rede instável estourava o timeout padrão de 30s no evento `load` da SPA da Gupy). Seletores inalterados.
> - **Idempotência do repositório (upsert por URL):** `salvar()` atualiza o registro quando a URL já existe, mantendo o pipeline re-executável sem violar a constraint unique — coberto pelo teste de integração `test_nao_deve_duplicar_vaga_com_mesma_url` (PostgreSQL real).
> - **Execução real:** `scripts/main.py` rodou de ponta a ponta (listagem → detalhe por vaga → upsert). Log do console listou as 12 vagas com trecho da descrição; consulta direta no PostgreSQL (`SELECT id, empresa, titulo, LENGTH(descricao) FROM vagas`) confirmou 12 linhas com descrições entre 2.275 e 7.514 caracteres.
> - Suíte final: **11 passed** (7 unitários + 4 integração).

## ⚪ Fase 4: Inteligência Artificial

- [ ] Integrar APIs de IA na camada de infraestrutura.
- [ ] Desenvolver os casos de uso de análise de perfil e mock interview.

## ⚪ Fase 5: Interface (FastAPI e HTMX)

- [ ] Criar rotas FastAPI (Presentation layer).
- [ ] Desenvolver templates e dashboard Kanban (Jinja2 + HTMX).

## ⚪ Fase 6: CI/CD e Finalização

- [ ] Configurar GitHub Actions (Lint, Testes automatizados).
- [ ] Revisão final de Clean Code e documentação do código.
