from __future__ import annotations

from datetime import date, timedelta

from app.config import LOAN_REMINDER_DAYS_BEFORE_DUE
from app.models.notification_log import NotificationLog


def schedule_due_reminders(member_id: str, loan_id: str, due_date: str) -> list[NotificationLog]:
    """FR-LNS-03, ASM-02: สร้าง log การแจ้งเตือนล่วงหน้า 1–3 วันก่อนกำหนดคืน ผ่าน channel email และ in_app"""

    target_date = date.fromisoformat(due_date)
    logs: list[NotificationLog] = []
    for offset in LOAN_REMINDER_DAYS_BEFORE_DUE:
        scheduled_date = target_date - timedelta(days=offset)
        for channel in ('email', 'in_app'):
            logs.append(
                NotificationLog(
                    notification_id=f'{loan_id}-{offset}-{channel}',
                    member_id=member_id,
                    loan_id=loan_id,
                    type='due_soon',
                    scheduled_at=scheduled_date.isoformat(),
                    sent_at=None,
                    channel=channel,
                    status='scheduled',
                )
            )
    return logs
