# Propostas de Tasks

Este arquivo registra propostas de alteracao de backlog antes de abrir uma task executavel.

O Codex deve sempre comunicar as mudancas propostas diretamente ao usuario, de forma simples, antes de codar. Quando a proposta for relevante para decisao futura, priorizacao, escopo ou auditoria, ela tambem deve ser registrada aqui.

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

Escopo sugerido:

- O que entraria.
- O que ficaria fora.

Impacto esperado:

- Beneficio pratico para o projeto.

Criterio para virar task:

- Condicao objetiva para mover a proposta para `docs/TASKS.md`.

Notas:

- Riscos, alternativas ou dependencias.
```

## PROP-001 - Manutencao do Gitleaks Action por Node 20

Status: Accepted

Motivacao:

- O GitHub Actions esta verde, mas emite aviso de deprecacao porque `gitleaks/gitleaks-action@v2` ainda roda em Node 20.

Escopo sugerido:

- Verificar versao atual recomendada da action.
- Atualizar `.github/workflows/quality-gates.yml` se houver versao compativel.
- Rodar quality gates e Gemini antes do commit.

Impacto esperado:

- Reduzir risco de falha futura do CI quando GitHub Actions remover suporte a Node 20.

Criterio para virar task:

- Usuario aprovar manutencao do CI ou pedir continuidade nessa frente.

Notas:

- Nao e bloqueante enquanto o workflow remoto continua passando.
- Aceita pelo usuario em 2026-05-28 para virar TASK-012.
