# Social Analytics Pipeline

Pipeline de engenharia de dados para coletar, normalizar, validar e orquestrar metricas de redes sociais.

Este repositorio sera construido por tasks pequenas, documentadas e auditaveis. O objetivo e evitar dependencia de memoria da conversa: o estado do projeto deve estar nos arquivos em `docs/` e nos logs gerados pelos scripts em `scripts/`.

## Fluxo de trabalho

Antes de codar uma task:

1. Revisar `docs/PLAN.md`, `docs/TASKS.md` e `docs/PROGRESS.md`.
2. Mostrar fase atual, task atual, riscos e conclusoes.
3. Explicar diretamente ao usuario as mudancas propostas, escopo, exclusoes e plano de validacao.
4. Registrar propostas relevantes em `docs/TASK_PROPOSALS.md`.
5. Declarar criterios de aceite e plano de teste.
6. Implementar somente depois desse checkpoint.
7. Atualizar documentacao e progresso.
8. Gerar pacote de revisao para o Gemini.

## Comandos uteis

```powershell
.\scripts\project_status.ps1
.\scripts\verify_docs.ps1
.\scripts\gemini_packet.ps1
python -m unittest discover -s tests
```

## Status

Fase atual: Fase 2 - Orquestracao e historico

Task atual: TASK-016 - Carregar DAG mockada no PostgreSQL

## Estrutura inicial

```text
src/social_analytics_pipeline/
  providers/   contratos de coleta por fonte social
  load/        carga idempotente em PostgreSQL
  pipeline/    orquestracao local do fluxo
  storage/     persistencia de payloads brutos
  transform/   schema normalizado e normalizadores por provider
data/fixtures/ fixtures raw dos providers mockados
db/init/       schema inicial do PostgreSQL local
tests/         testes automatizados
.github/       quality gates de CI
```
