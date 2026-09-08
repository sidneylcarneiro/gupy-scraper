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

## ✅ Fase 4: Inteligência Artificial (Concluída)

- [~] Integrar APIs de IA na camada de infraestrutura. *(Concluído: adaptador real `LLMAnalisador` com DeepSeek (SDK OpenAI, `base_url=https://api.deepseek.com`), validado contra a API com a `LLM_API_KEY`.)*
- [~] Desenvolver os casos de uso de análise de perfil e mock interview. *(Concluído: `AnalisarAderenciaUseCase`, `AnalisarPerfilCandidatoUseCase` (match E2E real executado) e `GerarMockInterviewUseCase` (5 perguntas reais geradas via DeepSeek).)*

> **Nota da Fase 4 (progresso):**
> - Port `IAnalisadorIA` (Protocol `@runtime_checkable`) em `application/interfaces/analisador_ia_port.py` com `extrair_palavras_chave(descricao_vaga: str) -> list[str]`.
> - Adaptador `LLMAnalisador` em `infrastructure/external_services/llm_analisador.py`: **DeepSeek via SDK da OpenAI** (`openai==3.*`, `base_url="https://api.deepseek.com"`, modelo `deepseek-chat`, `temperature=0.1`). Prompt solicita array JSON puro; limpeza de blocos markdown ` ```json `/` ``` ` antes do `json.loads`; `try/except` retorna `[]` em qualquer falha da API; retorna `[]` sem chamar a API para descrição vazia; `ValueError` quando `LLM_API_KEY` ausente.
> - Caso de uso `AnalisarAderenciaUseCase` em `application/use_cases/analisar_aderencia_vaga.py`: recebe `IVagaRepository` + `IAnalisadorIA` no construtor; `executar(url_vaga)` busca a vaga no repositório e passa a `descricao` para a IA; levanta `VagaNaoEncontradaError` (sem acionar a IA) quando a URL não existe.
> - TDD: **8 testes** do adaptador com `unittest.mock.patch` no client OpenAI (nada de rede): extração + kwargs da chamada (`model`, `temperature`, mensagens, base_url), limpeza de markdown `json`/simples, falha da API → `[]`, descrição vazia → `[]` sem chamar a API, `ValueError` sem key, key do `.env` e precedência da key explícita. 5 testes do use case com fakes. Suíte: **21 passed**.
> - `scripts/test_deepseek.py`: **EXECUTADO COM SUCESSO contra a API real do DeepSeek** — analisou a vaga "Pessoa Desenvolvedora Backend Python Especialista I (Venda Direta)" (Grupo Boticário) e retornou 43 palavras-chave técnicas e comportamentais (Python, Django, AWS, CI/CD, Scrum, GenAI, Clean Code, soft skills etc.).
> - **Correção de infraestrutura de testes**: os testes de integração usavam o MESMO banco de desenvolvimento e o `drop_all` do teardown apagava as vagas do pipeline. Agora usam o banco dedicado `gupy_scraper_test` (derivado da `DATABASE_URL`), isolando pytest dos dados reais. Suíte: **21 passed**.
> - **Match de perfil (item 2, otimização de custos):** port `IAnalisadorIA` ganhou `analisar_perfil(vaga_keywords, perfil_candidato) -> dict`; `LLMAnalisador.analisar_perfil` usa **prompt sistêmico mínimo** (4 linhas) exigindo JSON puro `{"aderentes": [...], "faltantes": [...]}`, `temperature=0.1`, normalização do parse (chaves ausentes → `[]`), `try/except` → `{}` e guarda-clause `{}` sem chamar a API para entradas vazias (zero tokens). Caso de uso `AnalisarPerfilCandidatoUseCase` (application/use_cases) delega ao port. TDD: 3 testes do use case com `AnalisadorFake` + 4 testes novos do adaptador com patch da OpenAI — **custo zero de tokens**. Suíte: **28 passed**.
> - **Entidade `PerfilCandidato`** (domain/entities/perfil.py): dataclass com `nome` e `resumo_experiencia`.
> - **Match E2E real executado** (`scripts/test_match_perfil.py`): vaga do Grupo Boticário (37 keywords) x perfil Sidney → **14 aderentes** (Python, Backend, LLMs, GenAI, CI/CD...) e **23 faltantes** (React, AWS, Django, testes...). Pipeline completo: PostgreSQL → extração de keywords → match via DeepSeek.
> - **Mock Interview (fechamento da Fase 4):** port `IAnalisadorIA` ganhou `gerar_perguntas_entrevista(titulo_vaga, habilidades_faltantes) -> list[str]`; `LLMAnalisador` usa prompt mínimo (5 linhas) exigindo array JSON puro, com limpeza de markdown, validação `isinstance(list)`, `try/except` → `[]` e guarda-clause sem chamar a API para entradas vazias. `GerarMockInterviewUseCase` (application/use_cases) delega ao port. TDD: 3 testes do use case (fakes) + 5 testes do adaptador (patch OpenAI, incl. markdown e resposta não-array) — custo zero. Execução real (`scripts/test_mock_interview.py`): 5 perguntas técnicas/comportamentais geradas sobre React, AWS, Testes e Scrum. **Nota:** scripts standalone precisam de `load_dotenv()` explícito (não importam `database`). Suíte final: **36 passed**.

> - **URL de Busca Dinâmica (feature arquitetural):** o contrato `IExtratorDeVagas.extrair_vagas(url_busca)` agora recebe a URL de busca como parâmetro; `GupyScraper` perdeu a constante fixa `URL_BUSCA` (navega para a URL recebida); `OrquestradorScraper.executar(url_busca)` repassa o parâmetro; `scripts/main.py` e `scripts/test_scraper.py` pedem a URL ao usuário via `input()`. A ferramenta aceita **qualquer URL de busca da Gupy** (cargo, filtros e modalidade definidos pelo usuário). Testes atualizados com `URL_BUSCA_FALSA` e nova verificação de propagação da URL ao scraper. Suíte: **36 passed**.

## ✅ Fase 5: Interface (FastAPI e HTMX) (Concluída)

- [x] Criar rotas FastAPI (Presentation layer). *(Concluído: painel em `presentation/app.py` com `GET /`, `POST /buscas`, `DELETE /buscas/{id}`, `POST /buscas/{id}/executar`, `GET /kanban` e `PATCH /vagas/{id}/status`, injeção de dependência via `Depends` para testes.)*
- [x] Desenvolver templates e dashboard Kanban (Jinja2 + HTMX). *(Concluído: formulário de buscas com apelido + lista HTMX; Kanban com 5 colunas do `StatusVaga`, drag-and-drop SortableJS dispara `PATCH` via `htmx.ajax` no `onEnd` e persiste no PostgreSQL automaticamente.)*

> **Nota da Fase 5 (progresso — URL dinâmica no painel):**
> - **Sem `input()` nem construtor de URL**: o usuário cadastra a busca no **painel web** informando a URL desejada e um **apelido**, persistida na nova tabela **`buscas`** para reuso e múltiplas buscas futuras.
> - Domínio: entidade `Busca(apelido, url, id)` + port `IBuscaRepository` (ABC). Infra: `BuscaModel` (apelido `unique`) + `PostgresBuscaRepository` (com `ApelidoJaExisteError`). Application: `CadastrarBuscaUseCase` (valida apelido obrigatório e URL `https://portal.gupy.io/`; normaliza espaços).
> - Presentation: FastAPI + Jinja2 + HTMX (CDN) em `presentation/app.py` + `presentation/templates/` (index + partial `lista_buscas.html`), com mensagens de sucesso/erro e confirm para remoção. `scripts/main.py` virou CLI por argumento (sem `input`).
> - TDD: 4 testes do use case (fakes), 3 de integração do repo (banco `gupy_scraper_test`) e 4 das rotas (TestClient + override de dependência). Suíte: **47 passed**. Smoke test real: servidor uvicorn na porta 8010 — cadastro via `POST /buscas` persistiu no PostgreSQL, URL inválida rejeitada e lista atualizada.
> - **Dashboard Kanban (fechamento da Fase 5):** port `IVagaRepository` ganhou `listar_todas()` e `atualizar_status(id, status)` (implementados no `PostgresVagaRepository`). Casos de uso `ListarVagasUseCase` e `AtualizarStatusVagaUseCase` (com `VagaNaoEncontradaError`). Rotas `GET /kanban` (vagas agrupadas por `StatusVaga`) e `PATCH /vagas/{id}/status` (retorna só o card via HTMX; status inválido rejeitado). `kanban.html` com 5 colunas e SortableJS (CDN): o `onEnd` do drag dispara `htmx.ajax('PATCH', ...)` e o banco é atualizado ao soltar o card. TDD: 3 testes dos use cases (fakes), 3 de integração (listar/atualizar/inexistente, banco de testes) e 3 novos de rota (Kanban, PATCH válido, PATCH inválido). Suíte: **56 passed**. Smoke test real: 5 colunas renderizadas com as 5 vagas do banco; `PATCH` da vaga 1 → `CANDIDATURA_ENVIADA` confirmado por consulta direta no PostgreSQL.
> - **Fix do bug do Kanban (status voltando ao original):** causa raiz dupla — (1) o upsert do `PostgresVagaRepository.salvar` sobrescrevia TODOS os campos no UPDATE, incluindo o status definido pelo usuário; agora o `_atualizar_modelo` preserva o `status` (definido apenas no INSERT); (2) cache do HTMX: `historyCacheSize: 0` via `<meta name="htmx-config">` nos templates e `Cache-Control: no-cache, no-store, must-revalidate` nas respostas de `GET /` e `GET /kanban`. TDD: teste RED `test_salvar_nao_deve_sobrescrever_status_de_vaga_existente` (reproduziu o bug antes do fix). Suíte: **57 passed**. Smoke test: headers de cache confirmados via curl; status preservado no PostgreSQL.

## ⚪ Fase 6: CI/CD e Finalização

- [ ] Configurar GitHub Actions (Lint, Testes automatizados).
- [ ] Revisão final de Clean Code e documentação do código.
