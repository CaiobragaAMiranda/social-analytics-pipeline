# Progresso

## Snapshot atual

Data: 2026-05-27

Fase atual: Fase 1 - Nucleo MVP e autenticacao

Task atual: TASK-004 - Criar schema unico de metricas

Status geral: iniciando normalizacao de payloads mockados para schema unico.

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

## Proximas acoes

- Criar commit da TASK-004.
- Iniciar TASK-005: criar carga local em PostgreSQL.
