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

Criterios de aceite:

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

- Pasta `<caminho-do-projeto>` criada.
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

## TASK-007 - Integrar fluxo local mock raw normalize load

Status: Done

Fase: Fase 1 - Nucleo MVP e autenticacao

Objetivo: conectar providers mockados, raw storage, normalizacao e loader em um fluxo local testavel.

Critérios de aceite:

- Orquestrador local executa provider -> raw storage -> normalizer -> loader.
- Fluxo funciona com providers mockados.
- Testes de integracao usam diretorio temporario e loader fake.
- Testes confirmam arquivos raw persistidos e metricas carregadas.
- Quality gates locais passam.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 19 testes executados com sucesso.
- Comando de lint: `ruff check .`
- Resultado de lint: aprovado.
- Comando de security lint: `bandit -c pyproject.toml -r src`
- Resultado de security lint: aprovado, sem issues.
- Comando de dependency audit: `pip-audit .`
- Resultado de dependency audit: sem vulnerabilidades conhecidas.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260528-000223.md`
- Resultado Gemini: aprovado.
- Commit: `feat: integrate local mock pipeline`

## TASK-008 - Adicionar Airflow via Docker

Status: Done

Fase: Fase 2 - Orquestracao e historico

Objetivo: adicionar ambiente local de Airflow via Docker Compose e uma DAG minima de smoke para validar a infraestrutura de orquestracao.

Critérios de aceite:

- Docker Compose contem servicos Airflow.
- `dags/` existe e e montado no Airflow.
- DAG minima de smoke criada.
- Bootstrap documenta init, startup, acesso e cleanup do Airflow.
- Quality gates locais passam.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Comando Docker Compose: `docker compose config`
- Resultado Docker Compose: configuracao valida.
- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 19 testes executados com sucesso.
- Comando de lint: `ruff check .`
- Resultado de lint: aprovado.
- Comando de security lint: `bandit -c pyproject.toml -r src`
- Resultado de security lint: aprovado, sem issues.
- Comando de dependency audit: `pip-audit .`
- Resultado de dependency audit: sem vulnerabilidades conhecidas.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260528-002654.md`
- Resultado Gemini: aprovado.
- Commit: `feat: add airflow docker environment`

## TASK-009 - Migrar fluxo local para DAG Airflow

Status: Done

Fase: Fase 2 - Orquestracao e historico

Objetivo: criar uma DAG Airflow que execute o fluxo local com providers mockados, raw storage, normalizacao e load em artefato JSON.

Critérios de aceite:

- DAG Airflow do pipeline mockado criada.
- DAG usa intervalo de dados do Airflow quando disponivel.
- Fluxo executa provider -> raw storage -> normalizer -> loader.
- Loader de artefato JSON e testavel sem Airflow.
- Bootstrap documenta a DAG e como aciona-la.
- Quality gates locais passam.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Comando Docker Compose: `docker compose config`
- Resultado Docker Compose: configuracao valida.
- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 22 testes executados com sucesso.
- Comando de lint: `ruff check .`
- Resultado de lint: aprovado.
- Comando de security lint: `bandit -c pyproject.toml -r src`
- Resultado de security lint: aprovado, sem issues.
- Comando de dependency audit: `pip-audit .`
- Resultado de dependency audit: sem vulnerabilidades conhecidas.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260528-085716.md`
- Resultado Gemini: aprovado.
- Commit: `feat: add airflow mock pipeline dag`

## TASK-010 - Configurar agendamento quinzenal e catchup historico

Status: Done

Fase: Fase 2 - Orquestracao e historico

Objetivo: configurar a DAG mockada para execucao quinzenal com catchup historico e artefatos identificaveis por intervalo de dados.

Critérios de aceite:

- DAG `social_analytics_mock_pipeline` usa agendamento quinzenal.
- DAG habilita catchup historico controlado.
- Configuracao de DAG e testavel sem importar Airflow.
- Artefatos processados incluem provider e intervalo de dados no nome.
- Bootstrap e arquitetura documentam schedule, catchup e backfill manual.
- Quality gates locais passam.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Comando Docker Compose: `docker compose config`
- Resultado Docker Compose: configuracao valida.
- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 24 testes executados com sucesso.
- Comando de lint: `ruff check .`
- Resultado de lint: aprovado.
- Comando de security lint: `bandit -c pyproject.toml -r src`
- Resultado de security lint: aprovado, sem issues.
- Comando de dependency audit: `pip-audit .`
- Resultado de dependency audit: sem vulnerabilidades conhecidas.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260528-091824.md`
- Resultado Gemini: aprovado.
- Commit: `feat: schedule airflow mock pipeline catchup`

## TASK-011 - Registrar propostas de mudanca antes da execucao

Status: Done

Fase: Fase 0 - Governanca do projeto

Objetivo: formalizar que o Codex deve sempre indicar mudancas propostas antes de codar e registrar propostas relevantes para decisao ou auditoria.

Criterios de aceite:

- Existe documento dedicado para propostas de tasks.
- README descreve que mudancas propostas devem ser explicadas diretamente ao usuario antes da implementacao.
- Contrato Gemini avalia se a proposta foi comunicada diretamente e se a task executada corresponde ao pedido do usuario.
- Progresso registra a mudanca de governanca.
- Verificacao documental passa.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260528-092656.md`
- Resultado Gemini: aprovado.
- Commit: `docs: add change proposal governance`

## TASK-012 - Preparar secret scan para Node 24 no GitHub Actions

Status: Done

Fase: Fase 1 - Nucleo MVP e autenticacao

Objetivo: remover o risco futuro do secret scan associado a deprecacao do Node 20 nos runners do GitHub Actions.

Criterios de aceite:

- Proposta `PROP-001` marcada como aceita.
- Workflow `quality-gates.yml` configura secret scan para usar Node 24 antecipadamente.
- Documentacao registra a decisao e a fonte oficial consultada.
- Quality gates locais relevantes passam.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Fonte oficial consultada: GitHub Changelog de deprecacao do Node 20 em GitHub Actions.
- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 24 testes executados com sucesso.
- Comando de lint: `ruff check .`
- Resultado de lint: aprovado.
- Comando de security lint: `bandit -c pyproject.toml -r src`
- Resultado de security lint: aprovado, sem issues.
- Comando de dependency audit: `pip-audit .`
- Resultado de dependency audit: sem vulnerabilidades conhecidas.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260528-093357.md`
- Resultado Gemini: aprovado.
- Commit: `ci: force node24 for secret scan action`

## TASK-013 - Conferir vazamento de informacao sensivel no prompt Gemini

Status: Done

Fase: Fase 0 - Governanca do projeto

Objetivo: garantir que o prompt de revisao do Gemini identifique vazamentos sensiveis em repositorios publicos antes de aprovar mudancas.

Criterios de aceite:

- O prompt do Gemini pede verificacao explicita de vazamentos sensiveis.
- O contrato do Gemini inclui vazamento sensivel como criterio de rejeicao.
- O bootstrap documenta o novo comportamento para repositorios publicos.
- Progresso registra a mudanca de governanca.
- Verificacao documental passa.
- Gemini revisa e aprova antes do commit.

Evidencias:

- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: `docs/REVIEWS/review-20260528-212740.md`
- Resultado Gemini: aprovado.
- Commit: `docs: harden gemini review for public repo leaks`

## TASK-014 - Padronizar severidade no feedback do Gemini

Status: In Progress

Fase: Fase 0 - Governanca do projeto

Objetivo: deixar o feedback do Gemini mais acionavel exigindo severidade, arquivo afetado, evidencia objetiva, risco pratico e acao recomendada em cada problema encontrado.

Criterios de aceite:

- O prompt do Gemini exige formato padronizado para cada problema.
- O contrato do Gemini registra o mesmo formato.
- O feedback continua proibido de repetir valores sensiveis.
- Verificacao documental passa.

Evidencias:

- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Revisao Gemini: pendente por reautenticacao do CLI.

## TASK-015 - Generalizar configuracoes sensiveis e hardcoded

Status: Done

Fase: Fase 0 - Governanca do projeto

Objetivo: conferir novamente vazamento de informacao sensivel e remover configuracoes locais hardcoded de credenciais, portas e caminhos quando fizer sentido.

Criterios de aceite:

- Varredura local nao encontra caminhos absolutos de usuario, chaves privadas, IPs privados ou segredos literais.
- Credenciais e portas locais do Docker Compose usam variaveis de ambiente.
- `.env.example` documenta as variaveis sem preencher senhas.
- `.env` local continua ignorado pelo Git.
- Bootstrap documenta uso de placeholders e alerta contra commit da saida expandida do Compose.
- Validacoes locais relevantes passam ou registram bloqueio operacional.

Evidencias:

- Varredura sensivel customizada: sem caminhos de usuario, chaves privadas, IPs privados ou segredos literais reais.
- Comando Docker Compose: `docker compose --env-file .env.example config --quiet`
- Resultado Docker Compose: configuracao valida.
- Comando de teste: `python -m unittest discover -s tests`
- Resultado de teste: 24 testes executados com sucesso fora do sandbox.
- Comando de lint: `ruff check .`
- Resultado de lint: aprovado.
- Comando de security lint: `bandit -c pyproject.toml -r src`
- Resultado de security lint: aprovado, sem issues.
- Comando de verificacao documental: `.\scripts\verify_docs.ps1`
- Resultado documental: verificacao concluida com sucesso.
- Gitleaks local: pendente porque o binario nao esta instalado neste ambiente; CI do GitHub mantem o secret scan.
- pip-audit local: pendente porque a execucao ficou presa neste ambiente.
- GitHub Actions: permissao `pull-requests: read` adicionada ao workflow para permitir secret scan em PR.
