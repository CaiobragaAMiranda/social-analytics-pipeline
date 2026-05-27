# Tasks

## Legenda

- Pending: ainda nao iniciada.
- In Progress: em execucao.
- Review: aguardando avaliacao do Gemini ou do usuario.
- Done: concluida e documentada.

## TASK-001 - Criar documentacao base e protocolo de automacao

Status: Done

Fase: Fase 0 - Governanca do projeto

Objetivo: criar a estrutura documental e scripts iniciais que permitam acompanhar progresso sem depender de memoria da conversa.

Critérios de aceite:

- `README.md` descreve o fluxo de trabalho.
- `docs/PLAN.md` contem fases do projeto.
- `docs/TASKS.md` registra backlog e task atual.
- `docs/PROGRESS.md` registra progresso inicial.
- `docs/BOOTSTRAP.md` explica como preparar o ambiente.
- `docs/ARCHITECTURE.md` registra arquitetura pretendida.
- `docs/GEMINI_CONTRACT.md` define rubrica de avaliacao.
- Scripts iniciais existem em `scripts/`.
- `scripts/verify_docs.ps1` executa com sucesso.

Evidencias:

- Comando de verificacao: `.\scripts\verify_docs.ps1`
- Resultado: verificacao documental concluida com sucesso.
- Comando de status: `.\scripts\project_status.ps1`
- Arquivos alterados: `README.md`, `docs/`, `scripts/`.

## TASK-002 - Criar esqueleto tecnico do projeto

Status: Done

Fase: Fase 1 - Nucleo MVP e autenticacao

Objetivo: criar a estrutura inicial de codigo Python para providers, raw storage, transformacoes e testes.

Critérios de aceite:

- Estrutura `src/` e `tests/` criada.
- Configuracao de projeto Python definida.
- Teste inicial executavel.
- README e bootstrap atualizados.

Evidencias:

- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 4 testes executados com sucesso.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Commit: `feat: add python project skeleton`

## TASK-001C - Criar primeiro commit da governanca

Status: Done

Fase: Fase 0 - Governanca do projeto

Objetivo: consolidar a documentacao e scripts de governanca em um commit inicial rastreavel.

Critérios de aceite:

- `docs/TASKS.md` registra TASK-001C.
- `docs/PROGRESS.md` registra a preparacao do primeiro commit.
- `scripts/verify_docs.ps1` executa com sucesso.
- Primeiro commit Git criado com a estrutura base.
- `git status --short` nao mostra mudancas pendentes apos o commit.

Evidencias:

- Comando de verificacao: `.\scripts\verify_docs.ps1`
- Resultado: verificacao documental concluida com sucesso.
- Commit: `chore: add project governance foundation`

## TASK-001B - Inicializar repositorio real em Programing

Status: Done

Fase: Fase 0 - Governanca do projeto

Objetivo: mover a estrutura base para o diretorio oficial do projeto e inicializar Git.

Critérios de aceite:

- Pasta `C:\Users\gamer\Desktop\Programing\social-analytics-pipeline` criada.
- `README.md`, `docs/` e `scripts/` copiados para a pasta oficial.
- Git inicializado na pasta oficial.
- `scripts/verify_docs.ps1` executa com sucesso na pasta oficial.
- `scripts/project_status.ps1` executa com sucesso na pasta oficial.

Evidencias:

- Comando de verificacao: `.\scripts\verify_docs.ps1`
- Comando de status: `.\scripts\project_status.ps1`
- Comando Git: `git status --short`

## TASK-001D - Automatizar revisao contratual com Gemini

Status: Done

Fase: Fase 0 - Governanca do projeto

Objetivo: configurar o Gemini CLI no terminal e criar um comando unico para revisar a task atual por contrato.

Critérios de aceite:

- Gemini CLI oficial instalado via `@google/gemini-cli`.
- Login com Google concluido.
- Wrapper local `scripts/gemini_cli.ps1` executa o CLI de forma reprodutivel.
- `scripts/gemini_review.ps1` gera pacote, chama o Gemini e salva resposta em `docs/REVIEWS/`.
- Gemini headless responde a uma chamada minima.

Evidencias:

- Versao validada: Gemini CLI `0.43.0`.
- Teste headless: resposta `GEMINI_OK`.
- Script criado: `scripts/gemini_review.ps1`.
- Revisao corrigida: `docs/REVIEWS/review-20260527-104706.md`.
- Resultado: aprovado / em conformidade.

## TASK-003 - Criar providers mockados

Status: Done

Fase: Fase 1 - Nucleo MVP e autenticacao

Objetivo: permitir desenvolvimento demonstravel sem depender de aprovacoes ou limites de APIs reais.

Critérios de aceite:

- Provider base definido.
- Providers mockados para Instagram, YouTube e TikTok.
- Fixtures de resposta raw.
- Testes de contrato dos providers.

Evidencias:

- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 8 testes executados com sucesso.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Commit: `feat: add mock social providers`

## TASK-004 - Criar schema unico de metricas

Status: Done

Fase: Fase 1 - Nucleo MVP e autenticacao

Objetivo: normalizar dados de redes sociais em formato tabular unico.

Critérios de aceite:

- Modelo de metricas documentado.
- Transformacoes por provider.
- Testes cobrindo campos obrigatorios e dados invalidos.

Evidencias:

- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 14 testes executados com sucesso.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260527-191357.md`
- Resultado Gemini: aprovado.
- Commit: `feat: add social metric normalizers`

## TASK-005 - Criar carga local em PostgreSQL

Status: Done

Fase: Fase 1 - Nucleo MVP e autenticacao

Objetivo: persistir metricas normalizadas em banco relacional local.

Critérios de aceite:

- Docker Compose com PostgreSQL.
- Script de migracao ou inicializacao.
- Upsert idempotente por chave natural.
- Teste ou verificacao local documentada.

Evidencias:

- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 17 testes executados com sucesso.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260527-193156.md`
- Resultado Gemini: aprovado.
- Commit: `feat: add postgres metric loading`

## TASK-006 - Adicionar quality gates de seguranca e CI

Status: Done

Fase: Fase 1 - Nucleo MVP e autenticacao

Objetivo: adicionar verificacoes automatizadas de qualidade, seguranca, dependencias e secrets para reduzir risco antes das proximas fases.

Critérios de aceite:

- Ruff configurado para lint local.
- Bandit configurado para security lint.
- pip-audit configurado para scan de dependencias.
- Gitleaks configurado para secret scan.
- GitHub Actions executa testes, lint, security lint, dependency audit e secret scan.
- Bootstrap documenta comandos locais.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 17 testes executados com sucesso.
- Comando de lint: `ruff check .`
- Resultado de lint: aprovado.
- Comando de security lint: `bandit -c pyproject.toml -r src`
- Resultado de security lint: aprovado, sem issues.
- Comando de dependency audit: `pip-audit .`
- Resultado de dependency audit: sem vulnerabilidades conhecidas.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260527-194742.md`
- Resultado Gemini: aprovado.
- Commit: `ci: add security quality gates`
