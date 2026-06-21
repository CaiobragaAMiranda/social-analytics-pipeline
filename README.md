# Social Analytics Pipeline

Data engineering pipeline for collecting, storing, normalizing, validating and orchestrating social media metrics.

The repository is the source of truth. Work is split into small, reviewable tasks so the project can continue without relying on long chat history.

## Current Status

- Phase: Local operations and consumption layer
- Current task: TASK-258 - Use catalog channels for deliberate collection
- Last completed delivery: TASK-257 - Add dashboard channel management panel
- Product state: the project has a channel-first static dashboard, real local YouTube and Instagram paths, safe fixture-based smoke flows, and optional Docker services for the dashboard, PostgreSQL and Airflow.

## Workflow

Before coding a task:

1. Review `docs/PLAN.md`, `docs/TASKS.md` and `docs/PROGRESS.md`.
2. Tell the user the proposed changes, scope, exclusions and validation plan.
3. Implement only after the user confirms or asks to continue.
4. Update documentation and progress.
5. Run local validation.
6. Batch up to five small tasks before committing and opening a PR.
7. Open a PR so GitHub Actions and CodeRabbit can review it.

Exceptions: commit and open a PR earlier when a task is large, risky, security-sensitive, blocks further work, or needs external review before continuing.

The detailed PR review rules are documented in `docs/REVIEW_POLICY.md`.

## Architecture

```text
YouTube API / Instagram API / TikTok fixtures
                    |
                Providers
                    |
              Raw Storage
                    |
      Normalizers and Validation
                    |
       JSON artifacts / PostgreSQL
                    |
        Reports / Static Dashboard
```

The real provider paths currently cover YouTube and authorized Instagram professional accounts. TikTok fixtures preserve the shared contract, but a real TikTok analytics integration remains intentionally deferred until an official path fits the channel-first model.

## SocialMetric Contract

`SocialMetric` is the normalized record used after provider collection and before validation, JSON artifact loading or PostgreSQL loading.

Required fields:

| Field | Meaning |
| --- | --- |
| `provider` | Source platform identifier: `youtube`, `instagram` or `tiktok`. |
| `account_id` | Provider account/channel identifier. |
| `content_id` | Provider content identifier. |
| `content_type` | Normalized content kind, such as `video`, `reel` or `post`. |
| `collected_at` | Timestamp for the collection interval end. |
| `raw_path` | Local reference to the stored raw payload. |

Optional fields:

| Group | Fields |
| --- | --- |
| Publication and engagement | `published_at`, `likes`, `comments`, `shares`, `views`, `followers` |
| Human-readable content | `title`, `thumbnail_url`, `content_url` |
| Human-readable channel | `channel_name`, `channel_image_url` |

Validation rejects blank required identifiers, negative numeric values and a publication timestamp later than its collection timestamp. Missing optional metrics remain `null`; the dashboard renders an explicit unavailable state instead of inventing a value.

| Provider | Main source fields | Contract mapping |
| --- | --- | --- |
| YouTube | `snippet`, `statistics`, channel metadata | Video ID, publish time, title, thumbnails, views, likes, comments and subscriber count. |
| Instagram | media object and authorized account metadata | Media ID, media type, timestamp, caption, permalink, media image, plays or impressions, engagements and profile metadata. |
| TikTok fixtures | item, author and metric objects | Item ID, creation time, play and engagement counters, and follower count. |

## Current Product Scope

The dashboard is a single-page, channel-first view: users choose a monitored channel, then see consolidated totals, platform source coverage, production activity and readable top content. Platforms are sources inside a channel rather than selector choices. The default smoke mode uses safe fixtures and no credentials; the optional Docker service exposes that same local dashboard and reports a container health state. For an existing artifact, set the local relative `DASHBOARD_OUTPUT` value and `DASHBOARD_NO_SMOKE=--no-smoke`.

YouTube v1 is closed. Instagram has a real local provider path with masked summaries and dashboard-compatible reports. The next implementation decision should prioritize a small operator or product improvement, not broad infrastructure expansion.

For detailed milestones and task evidence, see `docs/TASKS.md` and `docs/PROGRESS.md`. The final dashboard scope is recorded in `docs/DASHBOARD_V1_ACCEPTANCE.md`; the product objective and remaining usability gaps are in `docs/DASHBOARD_PRODUCT_BRIEF.md`; channel management is planned in `docs/CHANNEL_CATALOG.md`; the Instagram operational flow is in `docs/INSTAGRAM_LOCAL_RUNBOOK.md`.

## Useful Commands

```powershell
.\scripts\project_status.ps1
.\scripts\verify_docs.ps1
$env:PYTHONPATH = "src"; python -m unittest discover -s tests
ruff check .
bandit -c pyproject.toml -r src
serve-dashboard
python -m social_analytics_pipeline.cli.channel_catalog --list
docker compose --env-file .env.example up dashboard
docker compose --env-file .env.example config --quiet
```

## Project Layout

```text
src/social_analytics_pipeline/  Python package
dags/                           Airflow DAGs
db/init/                        PostgreSQL schema
data/fixtures/                  safe mock payloads
tests/                          automated tests
docs/                           compact project context
SKILLS.md                       engineering standards and daily checklist
scripts/                        status, docs and review helpers
```
