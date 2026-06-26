# Channel Catalog

## Purpose

The channel catalog defines which human channels the project monitors. A channel is one creator, brand or organization identity that may have YouTube, Instagram and TikTok sources.

The dashboard selects a catalog channel. Platforms are sources within that channel, not separate dashboard identities.

## Local-First Design

- The real catalog is local and ignored by Git.
- The repository ships only a safe example catalog with placeholders.
- The dashboard management panel uses a localhost-only catalog API to create, edit, enable, disable and remove entries without manual JSON editing. The Docker dashboard port is bound to localhost only.
- Saving a channel updates catalog configuration only. A separate `Collect now` action selects enabled configured sources and runs supported local provider dispatch.

## Catalog Contract

```json
{
  "channels": [
    {
      "id": "brand-channel",
      "name": "Brand Channel",
      "image_url": "",
      "schedule": "",
      "platforms": {
        "youtube": { "handle": "@channel", "enabled": true },
        "instagram": { "handle": "", "enabled": false },
        "tiktok": { "handle": "", "enabled": false }
      }
    }
  ]
}
```

`id` is a stable local identifier. `name`, `image_url` and `schedule` are user-facing metadata. `schedule` is empty, `daily` or `weekly`. A platform is collected only when it is enabled and has the configuration required by its official provider.

## Dashboard Behavior

- The management panel lists monitored channels with their names, images and source coverage.
- Users can add, edit, enable, disable or remove channels.
- Users can set a public image URL for each monitored channel.
- Users can add a public handle or URL for each platform source.
- Users can set collection intent to off, daily or weekly for each channel.
- Local CLI commands can update the same image, source reference and schedule fields for bootstrap automation.
- Source status is `ready` only when the source is enabled and has a public reference.
- `Collect now` records a local per-source status with last attempt, last success and safe outcome text.
- Ready YouTube and Instagram sources can run through their real local pipelines when local credentials are configured.
- Unsupported source dispatch is recorded as a safe failed outcome until that provider path is wired.
- A channel with no collected data remains visible with an explicit source state.
- Numeric metrics may render as `0` when zero is a valid value. Source coverage explains whether data is connected, unavailable or not monitored.

## Initial Exclusions

- No automatic collection when a channel is saved.
- No shared cloud catalog or multi-user authorization.
- No storage of API keys, access tokens, raw provider payloads or local paths in the catalog or status file.

## Collection Automation Roadmap

1. Wire TikTok only after an official analytics path fits this project.
2. Connect daily or weekly schedule intent to orchestration.
3. Reuse existing retry, token safety and failure reporting behavior for scheduled runs.
