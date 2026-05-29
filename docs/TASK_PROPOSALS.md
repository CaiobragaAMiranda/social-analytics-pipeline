# Propostas de Tasks

Este arquivo registra propostas de alteracao de backlog antes de abrir uma task executavel.

O Codex deve sempre comunicar as mudancas propostas diretamente ao usuario, de forma simples, antes de codar. Quando a mudanca envolver risco tecnico, decisao de design ou manutencao de longo prazo, ela deve ser registrada aqui.

## Regras

- Propostas nao sao compromissos de implementacao.
- Antes de iniciar codigo, o Codex deve explicar diretamente ao usuario a proposta de mudanca, escopo, exclusoes e plano de validacao.
- Propostas devem explicar motivacao, impacto, escopo e criterio de decisao.
- Uma proposta so vira task quando o usuario aprovar explicitamente ou pedir para seguir.
- Ao virar task, a proposta deve ser copiada ou resumida em `docs/TASKS.md` com status `In Progress`.
- Propostas rejeitadas ou adiadas devem permanecer registradas quando forem relevantes para contexto futuro.

## Template

```text
## PROP-000 - Titulo curto

Status: Proposed | Accepted | Deferred | Rejected

Motivacao:
- Por que essa mudanca foi sugerida.

Escopo:
- O que entraria.
- O que ficaria fora.

Impacto esperado:
- Beneficio pratico para o projeto.

Criterio para virar task:
- Condicao objetiva para mover a proposta para `docs/TASKS.md`.

Notas:
- Riscos, alternativas ou dependencias.
```

## PROP-001 - Forcar Node 24 no GitHub Actions para Secret Scan

Status: Accepted

Motivacao:
- O GitHub Actions esta depreciando o Node 20 nos runners.
- O Gitleaks Action pode falhar se o runner nao for forcado a usar um runtime mais recente.

Escopo:
- Adicionar `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"` ao workflow `quality-gates.yml`.

Criterio para virar task:
- Usuario aprovar manutencao do CI ou pedir continuidade nessa frente.

Notas:
- Aceita pelo usuario em 2026-05-28 para virar TASK-012.

## PROP-002 - Padronizacao de Feedback (TASK-014)

Status: Accepted

Motivacao:
- TASK-014: O feedback do Gemini precisa ser mais acionavel, seguindo uma estrutura de severidade, arquivo, evidencia, risco e acao.

Escopo:
- Atualizar `scripts/gemini_review.ps1`, `scripts/chatgpt_review.ps1` e `docs/AGENT_CONTRACTS.md` para exigir o novo formato de feedback (TASK-014).

Impacto esperado:
- Revisoes mais claras e acionaveis.

Criterio para virar task:
- Aprovacao do usuario para consolidar essa melhoria de governanca.

Notas:
- Aceito pelo usuario em 2026-05-29 para virar TASK-014.
