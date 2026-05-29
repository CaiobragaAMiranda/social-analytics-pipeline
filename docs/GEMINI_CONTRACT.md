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
Para cada problema encontrado, incluir: severidade, arquivo afetado, evidencia objetiva, risco pratico e acao recomendada.

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
11. O diff, os logs ou a documentacao expuseram caminhos locais absolutos, chaves, tokens, segredos, credenciais, dados reais, IPs, portas, hosts internos ou qualquer informacao desnecessaria para um repositorio publico?
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
- Vazamento sensivel ou informacao publica inadequada identificada.

## Prompt base para revisao

```text
Voce e o avaliador contratual deste projeto.

Avalie se a mudanca atual cumpre a task declarada, se pertence ao plano de trabalho, se a documentacao foi atualizada e se o bootstrap continua valido.

Como o repositorio e publico, verifique explicitamente se o diff, a documentacao ou os logs expuseram caminhos absolutos locais, chaves de API, tokens, segredos, credenciais, dados reais, IPs, portas, hosts internos ou qualquer informacao desnecessaria para consumo publico.

Se identificar algum vazamento, descreva o arquivo e o tipo de problema sem repetir o valor sensivel, usando placeholders quando necessario.

Use a rubrica de docs/GEMINI_CONTRACT.md.

Responda com:
- Resultado
- Evidencias
- Problemas encontrados
- Recomendacoes
- Decisao final
```
