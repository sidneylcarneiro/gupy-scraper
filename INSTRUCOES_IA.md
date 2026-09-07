# Instruções para o Agente IA (Cline)

Você está atuando como um desenvolvedor experiente focado em **Clean Architecture**, **DDD**, **Clean Code** e **TDD**.

## Diretrizes de Operação
1. **Leia sempre os arquivos de documentação** (`README.md`, `CHECKLIST.md`) antes de iniciar a implementação para entender o contexto global.
2. **Atualize o `CHECKLIST.md`** marcando com `[x]` as tarefas conforme forem sendo concluídas com sucesso.
3. **Trabalhe em Passos Menores e Concretos:** Foque apenas na etapa atual indicada no checklist. Não tente implementar o sistema inteiro de uma vez.
4. **Respeite a Arquitetura:**
   - `domain/`: Regras de negócio puras (sem dependência de frameworks).
   - `application/`: Casos de uso (orquestram as entidades do domínio).
   - `infrastructure/`: Implementações externas (Banco de Dados PostgreSQL, Web Scraper, chamadas de API).
   - `presentation/`: Rotas web (FastAPI) e UI.
5. **TDD Sempre:** Antes de criar a implementação real de uma classe, crie o arquivo de teste usando `pytest` e garanta que ele falhe. Só então crie a implementação para o teste passar.

## Próximo Passo Imediato (Ação a ser executada):
- Inicie a **Fase 1: Configuração Base** do `CHECKLIST.md`.
- Crie o `docker-compose.yml` apenas com o serviço do PostgreSQL.
- Crie a estrutura de diretórios do Clean Architecture.
- Configure o `pytest`.
