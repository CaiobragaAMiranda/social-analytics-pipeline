from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class SocialProvider(ABC):
    """Contract implemented by real and mock social data providers."""

    name: str

    @abstractmethod
    def collect_metrics(
        self,
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[dict[str, Any]]:
        """Collect raw metric payloads for an account and time interval."""
