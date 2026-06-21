# Channel Catalog

## Purpose

The channel catalog defines which human channels the project monitors. A channel is one creator, brand or organization identity that may have YouTube, Instagram and TikTok sources.

The dashboard selects a catalog channel. Platforms are sources within that channel, not separate dashboard identities.

## Local-First Design

- The real catalog is local and ignored by Git.
- The repository ships only a safe example catalog with placeholders.
- A future dashboard management panel uses a localhost-only catalog API to create, edit, enable, disable and remove entries without manual JSON editing. The Docker dashboard port is bound to localhost only.
- Saving a channel updates catalog configuration only. Collection remains a deliberate separate action in the first version.

## Catalog Contract

```json
{
  "channels": [
    {
      "id": "brand-channel",
      "name": "Brand Channel",
      "image_url": "",
      "platforms": {
        "youtube": { "handle": "@channel", "enabled": true },
        "instagram": { "handle": "", "enabled": false },
        "tiktok": { "handle": "", "enabled": false }
      }
    }
  ]
}
```

`id` is a stable local identifier. `name` and `image_url` are user-facing metadata. A platform is collected only when it is enabled and has the configuration required by its official provider.

## Dashboard Behavior

- The management panel lists monitored channels with their names, images and source coverage.
- Users can add, edit, enable, disable or remove channels.
- A channel with no collected data remains visible with an explicit source state.
- Numeric metrics may render as `0` when zero is a valid value. Source coverage explains whether data is connected, unavailable or not monitored.

## Initial Exclusions

- No automatic collection when a channel is saved.
- No shared cloud catalog or multi-user authorization.
- No storage of API keys, access tokens or raw provider payloads in the catalog.
