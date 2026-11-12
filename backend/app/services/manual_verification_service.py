from __future__ import annotations

from datetime import UTC, datetime

from app.models.access_event import AccessEvent
from app.models.manual_verification_audit import ManualVerificationAudit

# FR-ACC-06, DOM-PRV-01: บันทึกเหตุผลและผลการตรวจสอบสิทธิ์ด้วยมือเพื่อให้มี audit trail ที่ชัดเจน

AUDIT_LOG: list[ManualVerificationAudit] = []


def create_manual_verification_audit(
    event: AccessEvent,
    staff_id: str,
    reason: str,
    manual_approved: bool,
) -> ManualVerificationAudit:
    """FR-ACC-06: จัดเก็บ audit log ของเจ้าหน้าที่ที่ตรวจสอบสิทธิ์ด้วยมือ"""

    audit = ManualVerificationAudit(
        audit_id=f'audit-{event.access_event_id}',
        event_id=event.access_event_id,
        member_id=event.member_id,
        verified_by_staff_id=staff_id,
        verification_reason=reason or 'Manual verification',
        verified_at=datetime.now(UTC).isoformat(timespec='seconds'),
        approved_by_staff=manual_approved,
    )
    AUDIT_LOG.append(audit)
    event.actor_type = 'staff'
    event.staff_id = staff_id
    event.audit_note = reason or 'Manual verification'
    event.manual_verification_required = False
    if manual_approved:
        event.result_status = 'approved_manual'
    else:
        event.result_status = 'rejected_manual'
    return audit
