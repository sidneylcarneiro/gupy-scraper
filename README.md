# Assistente Automático de Carreira (Gupy Scraper) 🚀

Este projeto é uma ferramenta automatizada desenvolvida para busca, extração profunda e gestão de candidaturas para vagas de **Desenvolvedor Python Júnior (Foco: Remoto)** na plataforma Gupy. 

Além de facilitar a aplicação em vagas, este projeto serve como um robusto **portfólio de engenharia de software** com integração de Inteligência Artificial, seguindo rigorosos padrões da indústria.

## 🎯 Objetivo Principal
Automatizar o processo de candidatura na Gupy, desde a busca da vaga ideal até a preparação para a entrevista, utilizando raspagem de dados (Web Scraping) e Inteligência Artificial.

---

## 🏗️ Arquitetura e Padrões
Este projeto é construído com foco em qualidade de software, manutenibilidade e escalabilidade, adotando as seguintes práticas:
- **Clean Architecture & DDD (Domain-Driven Design):** Separação clara de responsabilidades em camadas (Domain, Application, Infrastructure, Presentation).
- **Clean Code:** Código legível, com nomes significativos e funções de responsabilidade única.
- **TDD (Test-Driven Development):** Desenvolvimento guiado por testes para garantir a confiabilidade desde o primeiro componente.
- **CI/CD:** Pipeline de integração e entrega contínuas via GitHub Actions.
- **Containerização:** Uso de Docker para orquestração da aplicação e do banco de dados.

## 🗺️ Roadmap e Funcionalidades

### Etapa 1: Motor de Extração (Scraping & Coleta de Dados) 🔍
- **Navegação Inteligente:** Acessa a URL filtrada da Gupy.
- **Extração Dinâmica e Profunda:** Captura de dados da listagem e dos links individuais das vagas.
- **Persistência e Segurança:** Armazenamento dos dados no **PostgreSQL** rodando em um container **Docker**. Autenticação isolada para chaves de API.

### Etapa 2: Motor de Inteligência e Análise (IA) 🧠
- **Análise de Requisitos (Match):** Processamento via IA para extrair palavras-chave vitais.
- **Mapeamento e Instruções:** Feedback sobre preenchimento do currículo e geração automatizada de "Cover Letters".

### Etapa 3: Interface e Gestão (Frontend) 💻
- **Interface Gráfica Web:** FastAPI, Jinja2 e HTMX.
- **Dashboard Kanban:** Gestão do funil de candidaturas.

### Etapa 4: Preparação e Posicionamento (Carreira) 🚀
- **Mock Interview e Marca Pessoal:** Simulações guiadas de entrevista e padronização do LinkedIn com base na vaga.

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python
- **Banco de Dados:** PostgreSQL (via Docker)
- **Design de Software:** Clean Architecture, DDD, TDD
- **DevOps:** Docker, Git/GitHub, CI/CD (GitHub Actions)
- **Backend/Frontend:** FastAPI, Jinja2, HTMX
- **Web Scraping:** Playwright / Selenium

---

## 👨‍💻 Autor
Desenvolvido por **[sidneylcarneiro](https://github.com/sidneylcarneiro)**.
