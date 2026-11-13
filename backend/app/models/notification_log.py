from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class NotificationLog:
    """รองรับ FR-LNS-03 และ ASM-02 สำหรับการแจ้งเตือนล่วงหน้า 1–3 วันก่อนกำหนดคืน"""

    notification_id: str
    member_id: str
    loan_id: str
    type: str
    scheduled_at: str | None
    sent_at: str | None = None
    channel: str = 'email'
    status: str = 'scheduled'

    def as_dict(self) -> dict[str, Any]:
        return {
            'notification_id': self.notification_id,
            'member_id': self.member_id,
            'loan_id': self.loan_id,
            'type': self.type,
            'scheduled_at': self.scheduled_at,
            'sent_at': self.sent_at,
            'channel': self.channel,
            'status': self.status,
        }
