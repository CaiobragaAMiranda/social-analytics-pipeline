from dataclasses import dataclass
from datetime import datetime, timezone
import json
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
        collected_at = record.collected_at.astimezone(timezone.utc)
        day = collected_at.strftime("%Y-%m-%d")
        stamp = collected_at.strftime("%H%M%S")
        target_dir = self.root_dir / record.provider / day
        target_dir.mkdir(parents=True, exist_ok=True)

        path = target_dir / f"{record.account_id}-{stamp}.json"
        path.write_text(
            json.dumps(record.payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path
