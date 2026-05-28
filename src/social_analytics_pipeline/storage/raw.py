import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RawRecord:
    provider: str
    account_id: str
    collected_at: datetime
    payload: dict[str, Any]


class RawStorage:
    """Persist raw API payloads before transformation."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir

    def save(self, record: RawRecord) -> Path:
        collected_at = record.collected_at.astimezone(UTC)
        day = collected_at.strftime("%Y-%m-%d")
        stamp = collected_at.strftime("%H%M%S")
        target_dir = self.root_dir / record.provider / day
        target_dir.mkdir(parents=True, exist_ok=True)

        payload_text = json.dumps(record.payload, ensure_ascii=False, indent=2, sort_keys=True)
        digest = sha256(payload_text.encode("utf-8")).hexdigest()[:12]
        path = target_dir / f"{record.account_id}-{stamp}-{digest}.json"
        path.write_text(
            payload_text,
            encoding="utf-8",
        )
        return path
