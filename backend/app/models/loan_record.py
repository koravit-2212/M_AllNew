from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LoanRecord:
    """รองรับ FR-LNS-02, FR-LNS-03, FR-LNS-05, FR-LNS-06 และ CON-LNS-02 สำหรับบันทึกข้อมูลการยืมและการคืน"""

    loan_id: str
    member_id: str
    copy_id: str
    borrow_time: str | None
    due_date: str | None
    return_time: str | None = None
    status: str = 'borrowed'
    overdue_days: int = 0
    penalty_amount: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            'loan_id': self.loan_id,
            'member_id': self.member_id,
            'copy_id': self.copy_id,
            'borrow_time': self.borrow_time,
            'due_date': self.due_date,
            'return_time': self.return_time,
            'status': self.status,
            'overdue_days': self.overdue_days,
            'penalty_amount': self.penalty_amount,
        }
