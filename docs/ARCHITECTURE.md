# Arquitetura

## Visao geral

O projeto sera um pipeline de analytics social com quatro camadas principais:

```text
Providers -> Raw Storage -> Transformacao -> Load/Validation -> Orquestracao
```

Na TASK-007 foi criado o primeiro orquestrador local:

```text
FixtureProvider
  -> RawStorage.save(...)
  -> normalize_payload(...)
  -> MetricLoader.load(...)
```

Esse fluxo e propositalmente independente de Postgres real durante os testes. O loader e um protocolo; em producao local, pode ser `PostgresMetricLoader`, e em teste pode ser um fake.

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

Na TASK-004 foi criado `normalize_payload`, que converte payloads raw enriquecidos pelos providers mockados para `SocialMetric`.

Mapeamento inicial:

```text
Instagram:
  id -> content_id
  media_type -> content_type
  like_count -> likes
  comments_count -> comments
  plays ou impressions -> views
  account.followers_count -> followers

YouTube:
  videoId -> content_id
  statistics.likeCount -> likes
  statistics.commentCount -> comments
  statistics.viewCount -> views
  channel.subscriberCount -> followers

TikTok:
  item_id -> content_id
  metrics.digg_count -> likes
  metrics.comment_count -> comments
  metrics.share_count -> shares
  metrics.play_count -> views
  author.follower_count -> followers
```

Provider desconhecido ou payload sem `_collection` deve falhar explicitamente com `ValueError`.

## Persistencia

O alvo inicial sera PostgreSQL via Docker Compose.

SQLite fica fora do caminho principal porque o projeto pretende demonstrar praticas mais proximas de ambiente produtivo.

Na TASK-005 foi criada a tabela `social_metrics` em `db/init/001_create_social_metrics.sql`.

Chave natural idempotente:

```text
provider + account_id + content_id + collected_at
```

O loader `PostgresMetricLoader` usa `INSERT ... ON CONFLICT ... DO UPDATE`, evitando duplicidade quando a mesma janela de coleta for reprocessada.

## Orquestracao

Airflow sera introduzido depois que extracao, transformacao e carga estiverem testadas localmente.

Antes do Airflow, `run_provider_pipeline` prova a integracao local das camadas. Isso reduz risco antes de migrar o fluxo para DAGs.

Na TASK-008 foi adicionado um ambiente Airflow local via Docker Compose.

Servicos principais:

```text
airflow-api-server
airflow-scheduler
airflow-dag-processor
airflow-worker
airflow-triggerer
airflow-init
airflow-postgres
airflow-redis
```

A primeira DAG e `social_analytics_smoke`, criada apenas para validar parse/executabilidade do ambiente. A migracao do fluxo `mock -> raw -> normalize -> load` para uma DAG real fica para a proxima task.

## Qualidade

Validacoes planejadas:

- Testes unitarios para transformacoes.
- Validacao de schema.
- Rejeicao ou DLQ para registros invalidos.
- Idempotencia no load.

## Quality Gates

Na TASK-006 foram adicionados quality gates de seguranca e dependencias:

```text
Ruff       -> lint Python
Bandit     -> security lint Python
pip-audit  -> scan de vulnerabilidades em dependencias
Gitleaks   -> secret scan
GitHub Actions -> execucao automatizada em push, pull request e workflow_dispatch
```

Detectores de N+1, race condition e memory leak ficam registrados como futuras evolucoes. Eles passam a fazer sentido quando houver ORM/leitura relacional, execucao concorrente com Airflow/Celery ou cargas grandes o bastante para profiling de memoria.
