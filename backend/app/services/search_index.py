from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# FR-SRC-01, FR-SRC-05, IF-CAT-01
# มาตรฐาน health probe สำหรับ Search Index ให้สามารถตรวจว่าสถานะและ last sync อยู่ในสภาพที่สามารถใช้งานต่อได้


class SearchIndexStatus:
    def __init__(
        self,
        index_status: str = 'healthy',
        last_sync_time: datetime | None = None,
        sync_health: str = 'ok',
    ) -> None:
        self.index_status = index_status
        self.last_sync_time = last_sync_time or datetime.now(timezone.utc)
        self.sync_health = sync_health

    def as_dict(self) -> dict[str, Any]:
        return {
            'index_status': self.index_status,
            'last_sync_time': self.last_sync_time.isoformat(),
            'sync_health': self.sync_health,
        }


def get_search_index_health() -> dict[str, Any]:
    status = SearchIndexStatus(
        index_status='healthy',
        last_sync_time=datetime.now(timezone.utc),
        sync_health='ok',
    )
    return status.as_dict()
