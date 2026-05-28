# Bootstrap

Este documento explica como preparar e verificar o projeto do zero.

## Caminho oficial do projeto

```powershell
cd C:\Users\gamer\Desktop\Programing\social-analytics-pipeline
```

## Pre-requisitos atuais

- Windows com PowerShell.
- Git.
- Python 3.12 ou superior.
- Docker Desktop, quando chegarmos ao PostgreSQL e Airflow.
- Node.js nao e requisito para este projeto no momento.

## Verificar ambiente

```powershell
git --version
python --version
docker --version
```

## Verificar status do projeto

```powershell
.\scripts\project_status.ps1
```

## Verificar documentacao minima

```powershell
.\scripts\verify_docs.ps1
```

## Rodar testes

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

O projeto ainda nao depende de pacotes externos na TASK-002. Isso mantem o bootstrap inicial simples e offline.

## Subir PostgreSQL local

```powershell
docker compose up -d postgres
docker compose ps
```

DSN local padrao:

```text
postgresql://social_analytics:social_analytics@localhost:5432/social_analytics
```

O schema inicial fica em `db/init/001_create_social_metrics.sql` e e aplicado automaticamente quando o volume do Postgres e criado pela primeira vez.

Para reiniciar o banco do zero durante desenvolvimento:

```powershell
docker compose down -v
docker compose up -d postgres
```

## Subir Airflow local

Prepare o arquivo `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Inicialize o banco/metadados do Airflow:

```powershell
docker compose up airflow-init
```

Suba os servicos principais:

```powershell
docker compose up -d airflow-api-server airflow-scheduler airflow-dag-processor airflow-worker airflow-triggerer
```

A interface fica em:

```text
http://localhost:8080
```

Credenciais locais:

```text
usuario: airflow
senha: airflow
```

Validar containers:

```powershell
docker compose ps
```

Limpar ambiente Airflow local:

```powershell
docker compose down --volumes --remove-orphans
```

## Validar providers mockados

Os providers mockados usam fixtures locais e nao precisam de tokens:

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_mock_providers
```

## Validar normalizacao para schema unico

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_normalizer
```

## Validar carga PostgreSQL sem banco real

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_postgres_loader
```

## Validar fluxo local integrado

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_local_pipeline
```

## Instalar ferramentas de desenvolvimento

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Rodar quality gates locais

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
ruff check .
bandit -c pyproject.toml -r src
pip-audit .
```

Secret scan local com Gitleaks depende do binario instalado na maquina:

```powershell
gitleaks detect --source . --config .gitleaks.toml
```

No GitHub, o workflow `.github/workflows/quality-gates.yml` executa testes, Ruff, Bandit, pip-audit e Gitleaks.

## Gerar pacote para Gemini

```powershell
.\scripts\gemini_packet.ps1
```

O pacote sera impresso no terminal para ser enviado ao Gemini. Em uma fase posterior, poderemos salvar esse pacote em `docs/REVIEWS/`.

## Rodar revisao contratual com Gemini

```powershell
.\scripts\gemini_review.ps1
```

Esse comando gera o pacote de revisao, chama o Gemini CLI em modo headless e salva a resposta em `docs/REVIEWS/`.
