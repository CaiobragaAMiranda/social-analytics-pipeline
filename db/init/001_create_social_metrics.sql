CREATE TABLE IF NOT EXISTS social_metrics (
    id BIGSERIAL PRIMARY KEY,
    provider TEXT NOT NULL,
    account_id TEXT NOT NULL,
    content_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    published_at TIMESTAMPTZ,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    views INTEGER,
    followers INTEGER,
    raw_path TEXT NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT social_metrics_natural_key UNIQUE (
        provider,
        account_id,
        content_id,
        collected_at
    )
);

CREATE INDEX IF NOT EXISTS idx_social_metrics_provider_collected_at
    ON social_metrics (provider, collected_at);

CREATE INDEX IF NOT EXISTS idx_social_metrics_account_content
    ON social_metrics (account_id, content_id);
