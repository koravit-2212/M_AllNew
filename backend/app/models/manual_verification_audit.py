from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ManualVerificationAudit:
    """FR-ACC-06: บันทึกผลการตรวจสอบสิทธิ์ด้วยมือของเจ้าหน้าที่เพื่อประกันความถูกต้องและความโปร่งใส"""

    audit_id: str
    event_id: str
    member_id: str | None = None
    verified_by_staff_id: str = ''
    verification_reason: str = ''
    verified_at: str = ''
    approved_by_staff: bool = False
