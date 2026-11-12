from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class AccessEvent:
    """FR-ACC-01, FR-ACC-03, FR-ACC-04, FR-ACC-05, FR-ACC-06: ประวัติการสแกนและผลลัพธ์การยืนยันตัวตนของผู้ใช้บริการ"""

    access_event_id: str
    member_id: str | None = None
    scan_method: str = 'qr'
    scanned_at: str = ''
    result_status: str = 'pending_verification'
    reason_code: str | None = None
    manual_verification_required: bool = False
    actor_type: str = 'member'
    staff_id: str | None = None
    audit_note: str | None = None

    @classmethod
    def create(cls, member_id: str, scan_method: str) -> 'AccessEvent':
        """FR-ACC-01: สร้าง event ใหม่ให้ตรงกับ contract ของการยืนยันตัวตนและบันทึก log"""

        return cls(
            access_event_id=f'acc-{datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")}',
            member_id=member_id,
            scan_method=scan_method,
            scanned_at=datetime.now(UTC).isoformat(timespec='seconds'),
            result_status='pending_verification',
        )
