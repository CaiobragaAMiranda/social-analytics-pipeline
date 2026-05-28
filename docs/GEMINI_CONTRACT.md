# Contrato de Revisao do Gemini

O Gemini atua como avaliador contratual do projeto. Ele deve avaliar documentos, diff, logs e criterios de aceite, nao memoria informal da conversa.

## Entrada recomendada

Para cada revisao, fornecer:

- `docs/PLAN.md`
- `docs/TASKS.md`
- `docs/TASK_PROPOSALS.md`, quando houver proposta relacionada.
- `docs/PROGRESS.md`
- `docs/BOOTSTRAP.md`
- `docs/ARCHITECTURE.md`
- Diff atual do Git, quando existir.
- Logs de teste ou verificacao.

## Rubrica

O Gemini deve responder:

```text
Resultado: Approved | Approved with notes | Changes requested

1. A task pertence ao plano?
2. Os criterios de aceite foram cumpridos?
3. A documentacao foi atualizada?
4. O bootstrap continua correto?
5. Existem mudancas fora do escopo?
6. Existem riscos tecnicos nao registrados?
7. Existem testes ou justificativa para ausencia de testes?
8. O progresso foi registrado de forma retomavel?
9. As mudancas propostas foram comunicadas diretamente ao usuario antes da implementacao?
10. A task executada corresponde a uma proposta aprovada ou a uma continuidade solicitada pelo usuario?
```

## Regras de aprovacao

Approved:

- Todos os criterios relevantes foram atendidos.
- Nao ha risco bloqueante.
- Documentacao e progresso estao coerentes.

Approved with notes:

- A task esta aceitavel, mas ha melhorias ou riscos nao bloqueantes.

Changes requested:

- Criterios de aceite nao cumpridos.
- Mudanca fora do escopo.
- Falta documentacao essencial.
- Bootstrap ou verificacao quebrados.

## Prompt base para revisao

```text
Voce e o avaliador contratual deste projeto.

Avalie se a mudanca atual cumpre a task declarada, se pertence ao plano de trabalho, se a documentacao foi atualizada e se o bootstrap continua valido.

Use a rubrica de docs/GEMINI_CONTRACT.md.

Responda com:
- Resultado
- Evidencias
- Problemas encontrados
- Recomendacoes
- Decisao final
```
