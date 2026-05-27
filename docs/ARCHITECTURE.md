# Arquitetura

## Visao geral

O projeto sera um pipeline de analytics social com quatro camadas principais:

```text
Providers -> Raw Storage -> Transformacao -> Load/Validation -> Orquestracao
```

## Providers

Responsaveis por coletar dados de cada fonte social.

Fontes planejadas:

- Instagram.
- YouTube.
- TikTok.
- Mock providers para desenvolvimento e demonstracao.

## Raw Storage

Toda resposta bruta sera preservada antes de qualquer transformacao.

Formato inicial previsto:

```text
data/raw/{provider}/{yyyy-mm-dd}/{entity_id}.json
```

Motivos:

- Auditoria.
- Reprocessamento.
- Debugging.
- Comparacao entre resposta bruta e dado normalizado.

## Schema Unico

As respostas diferentes das APIs serao normalizadas para uma estrutura comum de metricas.

Campos candidatos:

- provider.
- account_id.
- content_id.
- content_type.
- collected_at.
- published_at.
- likes.
- comments.
- shares.
- views.
- followers.
- raw_path.

## Persistencia

O alvo inicial sera PostgreSQL via Docker Compose.

SQLite fica fora do caminho principal porque o projeto pretende demonstrar praticas mais proximas de ambiente produtivo.

## Orquestracao

Airflow sera introduzido depois que extracao, transformacao e carga estiverem testadas localmente.

## Qualidade

Validacoes planejadas:

- Testes unitarios para transformacoes.
- Validacao de schema.
- Rejeicao ou DLQ para registros invalidos.
- Idempotencia no load.
