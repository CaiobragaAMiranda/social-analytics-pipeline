# Social Analytics Pipeline

Pipeline de engenharia de dados para coletar, normalizar, validar e orquestrar metricas de redes sociais.

Este repositorio sera construido por tasks pequenas, documentadas e auditaveis. O objetivo e evitar dependencia de memoria da conversa: o estado do projeto deve estar nos arquivos em `docs/` e nos logs gerados pelos scripts em `scripts/`.

## Fluxo de trabalho

Antes de codar uma task:

1. Revisar `docs/PLAN.md`, `docs/TASKS.md` e `docs/PROGRESS.md`.
2. Mostrar fase atual, task atual, riscos e conclusoes.
3. Declarar criterios de aceite e plano de teste.
4. Implementar somente depois desse checkpoint.
5. Atualizar documentacao e progresso.
6. Gerar pacote de revisao para o Gemini.

## Comandos uteis

```powershell
.\scripts\project_status.ps1
.\scripts\verify_docs.ps1
.\scripts\gemini_packet.ps1
python -m unittest discover -s tests
```

## Status

Fase atual: Fase 1 - Nucleo MVP e autenticacao

Task atual: TASK-002 - Criar esqueleto tecnico do projeto

## Caminho oficial

```text
C:\Users\gamer\Desktop\Programing\social-analytics-pipeline
```

## Estrutura inicial

```text
src/social_analytics_pipeline/
  providers/   contratos de coleta por fonte social
  storage/     persistencia de payloads brutos
  transform/   schema normalizado inicial
data/fixtures/ fixtures raw dos providers mockados
tests/         testes automatizados
```
