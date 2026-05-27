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
