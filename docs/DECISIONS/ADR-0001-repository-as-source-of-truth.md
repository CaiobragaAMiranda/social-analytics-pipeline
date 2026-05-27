# ADR-0001 - Repositorio como fonte da verdade

Status: Accepted

Data: 2026-05-27

## Contexto

O projeto sera construido em colaboracao entre usuario, Codex e Gemini. Conversas longas podem perder contexto ou ficar caras de manter.

## Decisao

Usaremos o repositorio como fonte da verdade. Plano, tasks, progresso, bootstrap, arquitetura e revisoes devem viver em arquivos versionaveis.

## Consequencias

Beneficios:

- Contexto retomavel.
- Revisao objetiva pelo Gemini.
- Menos dependencia de memoria de conversa.
- Melhor rastreabilidade de progresso.

Custos:

- Toda task precisa atualizar documentacao.
- Pequenas mudancas exigem disciplina de registro.
