# Progresso

## Snapshot atual

Data: 2026-05-27

Fase atual: Fase 2 - Orquestracao e historico

Task atual: TASK-008 - Adicionar Airflow via Docker

Status geral: iniciando ambiente Airflow local via Docker Compose.

## Registro

### 2026-05-27

- Definido que o projeto sera construido por tasks pequenas e auditaveis.
- Definido que Codex deve apresentar estado, conclusoes, criterios de aceite e plano de teste antes de codar.
- Definido que Gemini atuara como avaliador contratual, usando documentos do repositorio, diff e logs.
- Iniciada TASK-001 para criar documentacao base e scripts de automacao.
- Criados `README.md`, `docs/PLAN.md`, `docs/TASKS.md`, `docs/PROGRESS.md`, `docs/BOOTSTRAP.md`, `docs/ARCHITECTURE.md`, `docs/GEMINI_CONTRACT.md` e `docs/DECISIONS/ADR-0001-repository-as-source-of-truth.md`.
- Criados scripts `scripts/project_status.ps1`, `scripts/verify_docs.ps1` e `scripts/gemini_packet.ps1`.
- Executada verificacao documental com sucesso.
- TASK-001 marcada como Done.
- Criada pasta oficial `C:\Users\gamer\Desktop\Programing\social-analytics-pipeline`.
- Copiados `README.md`, `docs/` e `scripts/` para a pasta oficial.
- Inicializado Git na pasta oficial.
- TASK-001B marcada como Done.
- Iniciada TASK-001C para criar o primeiro commit rastreavel da governanca.
- Executada verificacao documental com sucesso para TASK-001C.
- TASK-001C marcada como Done.
- Publicado repositorio privado no GitHub: `https://github.com/CaiobragaAMiranda/social-analytics-pipeline`.
- Iniciada TASK-002 para criar o esqueleto tecnico Python.
- Criado `pyproject.toml` com metadados do projeto Python.
- Criada estrutura `src/social_analytics_pipeline/` com config, providers, storage e transform.
- Criado teste inicial em `tests/test_project_skeleton.py`.
- Atualizados `README.md`, `docs/BOOTSTRAP.md` e `docs/ARCHITECTURE.md`.
- Executados 4 testes unitarios com sucesso.
- Executada verificacao documental com sucesso.
- TASK-002 marcada como Done.
- Commit da TASK-002 publicado no GitHub: `bd29c8c feat: add python project skeleton`.
- Iniciada TASK-003 para criar providers mockados.
- Criadas fixtures raw para Instagram, YouTube e TikTok em `data/fixtures/`.
- Criado `FixtureProvider` e factory `build_mock_providers`.
- Criados testes de contrato em `tests/test_mock_providers.py`.
- Executados 8 testes unitarios com sucesso.
- Executada verificacao documental com sucesso.
- TASK-003 marcada como Done.
- Configurado Gemini CLI oficial `@google/gemini-cli`.
- Login com Google concluido no Gemini CLI.
- Criados `scripts/gemini_cli.ps1` e `scripts/gemini_review.ps1`.
- Gemini headless validado com resposta `GEMINI_OK`.
- TASK-001D marcada como Done.
- Primeira tentativa de revisao Gemini falhou porque o agente tentou chamar `run_shell_command`, ferramenta indisponivel no ambiente.
- Corrigido `scripts/gemini_review.ps1` para modo avaliador textual com `--approval-mode plan` e instrucao explicita para nao usar ferramentas.
- Revisao Gemini salva em `docs/REVIEWS/review-20260527-104706.md`.
- Resultado Gemini: aprovado / em conformidade.
- Commit da TASK-003 e automacao Gemini publicado no GitHub: `08bfeb4 feat: add mock providers and gemini review automation`.
- Iniciada TASK-004 para criar normalizacao dos payloads mockados em `SocialMetric`.
- Criado `src/social_analytics_pipeline/transform/normalizer.py`.
- Criados normalizadores para Instagram, YouTube e TikTok.
- Criados testes de transformacao em `tests/test_normalizer.py`.
- Executados 14 testes unitarios com sucesso.
- Executada verificacao documental com sucesso.
- Primeira revisao Gemini da TASK-004 falhou porque o wrapper local nao encaminhou o pacote para `stdin`.
- Corrigido `scripts/gemini_cli.ps1` para repassar entrada padrao ao CLI.
- Revisao Gemini formal salva em `docs/REVIEWS/review-20260527-191357.md`.
- Resultado Gemini: aprovado.
- TASK-004 marcada como Done.
- Commit da TASK-004 publicado no GitHub: `2b716f7 feat: add social metric normalizers`.
- Iniciada TASK-005 para criar carga local em PostgreSQL.
- Criado `docker-compose.yml` com servico PostgreSQL 16.
- Criado schema inicial em `db/init/001_create_social_metrics.sql`.
- Criado `PostgresMetricLoader` com upsert idempotente.
- Criados testes unitarios em `tests/test_postgres_loader.py`.
- Adicionada dependencia `psycopg[binary]` ao `pyproject.toml`.
- Corrigido `raw_path` do loader para persistir paths em formato POSIX estavel.
- Executados 17 testes unitarios com sucesso.
- Executada verificacao documental com sucesso.
- Revisao Gemini `docs/REVIEWS/review-20260527-192800.md` falhou porque `gemini_packet.ps1` imprimia cabecalhos com `Write-Host`, deixando o pacote vazio para o pipeline.
- Corrigido `scripts/gemini_packet.ps1` para emitir conteudo com `Write-Output` e incluir diff completo do repositorio.
- Revisao Gemini `docs/REVIEWS/review-20260527-192923.md` falhou porque `scripts/gemini_cli.ps1` nao recebia pipeline via `[Console]::In`.
- Mantido `scripts/gemini_cli.ps1` como wrapper simples para chamadas diretas.
- Corrigido `scripts/gemini_review.ps1` para enviar o pacote ao Gemini por arquivo temporario e `cmd /c type`, evitando perda de `stdin` em wrappers PowerShell.
- Revisao Gemini `docs/REVIEWS/review-20260527-193101.md` aprovou a TASK-005, mas recomendou incluir arquivos novos ainda nao rastreados no pacote.
- Corrigido `scripts/gemini_packet.ps1` para incluir diff staged e conteudo de arquivos untracked.
- Revisao Gemini final salva em `docs/REVIEWS/review-20260527-193156.md`.
- Resultado Gemini: aprovado.
- TASK-005 marcada como Done.
- Commit da TASK-005 publicado no GitHub: `59f9aa5 feat: add postgres metric loading`.
- Iniciada TASK-006 para adicionar quality gates de seguranca e CI.
- Versoes de GitHub Actions verificadas em fontes oficiais em 2026-05-27:
  - `actions/checkout@v6`.
  - `actions/setup-python@v6`.
  - `gitleaks/gitleaks-action@v2`.
  - `pypa/gh-action-pip-audit@v1.1.0`.
- Adicionadas dependencias dev para `ruff`, `bandit` e `pip-audit`.
- Adicionada configuracao `.gitleaks.toml`.
- Criado workflow `.github/workflows/quality-gates.yml`.
- Documentados comandos locais de quality gates no bootstrap.
- Instaladas dependencias dev via `python -m pip install -r requirements-dev.txt`.
- Primeira execucao do Ruff encontrou divida de formatacao/imports em codigo existente.
- Aplicado `ruff check . --fix` e ajustes manuais de linhas longas.
- Executados 17 testes unitarios com sucesso.
- Ruff aprovado com `All checks passed!`.
- Bandit aprovado sem issues.
- pip-audit aprovado sem vulnerabilidades conhecidas.
- Verificacao documental concluida com sucesso.
- Revisao Gemini salva em `docs/REVIEWS/review-20260528-002654.md`.
- Resultado Gemini: aprovado.
- TASK-008 marcada como Done.
- Revisao Gemini salva em `docs/REVIEWS/review-20260528-000223.md`.
- Resultado Gemini: aprovado.
- TASK-007 marcada como Done.
- Commit da TASK-007 publicado no GitHub: `31b0795 feat: integrate local mock pipeline`.
- GitHub Actions `Quality Gates` concluiu com sucesso.
- Consultada documentacao oficial do Apache Airflow 3.2.1 para Docker Compose.
- Iniciada TASK-008 para adicionar Airflow via Docker.
- Criados servicos Airflow em `docker-compose.yml`.
- Criada DAG smoke em `dags/social_analytics_smoke_dag.py`.
- Criado `.env.example` com `AIRFLOW_UID=50000`.
- Primeira validacao `docker compose config` falhou porque o anchor comum estava como `airflow-common`; corrigido para `x-airflow-common`.
- Atualizada allowlist do Gitleaks para credenciais locais documentadas do Airflow (`airflow/airflow`).
- `docker compose config` validado com sucesso.
- Executados 19 testes unitarios com sucesso.
- Ruff aprovado.
- Bandit aprovado sem issues.
- pip-audit aprovado sem vulnerabilidades conhecidas.
- Verificacao documental concluida com sucesso.
- Revisao Gemini salva em `docs/REVIEWS/review-20260527-194742.md`.
- Resultado Gemini: aprovado.
- TASK-006 marcada como Done.
- Commit da TASK-006 publicado no GitHub: `bd85b3d ci: add security quality gates`.
- GitHub Actions `Quality Gates` concluiu com sucesso.
- Iniciada TASK-007 para integrar provider mockado, raw storage, normalizacao e loader.
- Criado `src/social_analytics_pipeline/pipeline/local.py`.
- Criado protocolo `MetricLoader` para desacoplar orquestracao do destino real.
- Criado teste de integracao em `tests/test_local_pipeline.py`.
- Teste de integracao encontrou colisao no nome de arquivos raw quando varios payloads eram salvos no mesmo segundo.
- Corrigido `RawStorage` para incluir hash curto do payload no nome do arquivo.
- Executados 19 testes unitarios com sucesso.
- Ruff aprovado.
- Bandit aprovado sem issues.
- pip-audit aprovado sem vulnerabilidades conhecidas.
- Verificacao documental concluida com sucesso.

## Proximas acoes

- Criar commit da TASK-008.
- Iniciar TASK-009: migrar fluxo local para DAG Airflow.
