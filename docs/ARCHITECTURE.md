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

Contrato inicial:

```text
SocialProvider.collect_metrics(account_id, start_at, end_at) -> list[dict]
```

Esse contrato ainda retorna payloads brutos. A normalizacao fica em `transform/`.

Na TASK-003 foram criados providers mockados baseados em fixtures:

```text
data/fixtures/instagram_metrics.json
data/fixtures/youtube_metrics.json
data/fixtures/tiktok_metrics.json
```

Os mocks preservam formatos diferentes por plataforma. Isso e intencional: a proxima etapa de transformacao deve provar que consegue mapear essas formas distintas para `SocialMetric`.

## Raw Storage

Toda resposta bruta sera preservada antes de qualquer transformacao.

Formato inicial previsto:

```text
data/raw/{provider}/{yyyy-mm-dd}/{entity_id}.json
```

Na TASK-002 foi criada a classe `RawStorage`, responsavel por persistir payloads JSON em disco.

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

Na TASK-002 foi criado o dataclass `SocialMetric` com esses campos candidatos iniciais.

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
