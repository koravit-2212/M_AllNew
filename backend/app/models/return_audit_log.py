from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ReturnAuditLog:
    """รองรับ FR-LNS-06 และ CON-LNS-02 สำหรับบันทึกเหตุการณ์คืนเกินกำหนดและค่าปรับให้เจ้าหน้าที่ตรวจสอบ"""

    audit_id: str
    loan_id: str
    member_id: str
    overdue_days: int
    penalty_amount: int
    processed_at: str | None
    actor: str

    def as_dict(self) -> dict[str, Any]:
        return {
            'audit_id': self.audit_id,
            'loan_id': self.loan_id,
            'member_id': self.member_id,
            'overdue_days': self.overdue_days,
            'penalty_amount': self.penalty_amount,
            'processed_at': self.processed_at,
            'actor': self.actor,
        }
