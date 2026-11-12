from __future__ import annotations

from app.models.access_event import AccessEvent
from app.models.facility_occupancy import AccessStore
from app.repositories.access_repository import AccessRepository
from app.services.external_id_service import ExternalIdentityVerificationError, verify_external_member_id
from app.services.member_profile_seed import access_status_for_member, find_member, is_eligible_for_access

# FR-ACC-01, FR-ACC-02, FR-ACC-03, IF-STD-01, CON-ELG-01, DOM-PRV-01
# Service นี้รวม logic ตรวจบัตร/QR, ตรวจสิทธิ์, บันทึก event และอัปเดต currentOccupancy สำหรับ AC-ACC-01


class AccessDenied(Exception):
    """FR-ACC-05, FR-ACC-06: สถานะไม่อนุญาตให้เข้าห้องสมุด พร้อมสาเหตุแยกตามเคสของการปฏิเสธ"""

    def __init__(self, status: str, message: str | None = None):
        self.status = status
        self.message = message or status
        super().__init__(self.message)


class AccessScanUnreadable(Exception):
    """ระบบอ่านสแกนได้ไม่ครบถ้วนหรือไม่สามารถยืนยันตัวตนได้"""


DENIAL_MESSAGES = {
    'not_found': 'ไม่พบข้อมูล',
    'no_eligibility': 'ไม่มีสิทธิ์',
    'verification_failed': 'ไม่สามารถตรวจสอบสิทธิ์ได้',
}


def _record_denied_event(store: AccessStore, member_id: str, scan_method: str, reason_code: str) -> AccessEvent:
    """FR-ACC-05: บันทึก event ที่ปฏิเสธด้วยเหตุผลที่ชัดเจนเพื่อให้เจ้าหน้าที่ตรวจสอบได้"""

    event = AccessEvent.create(member_id, scan_method)
    event.member_id = member_id
    event.result_status = reason_code
    event.reason_code = reason_code
    event.manual_verification_required = True
    event.audit_note = DENIAL_MESSAGES.get(reason_code, 'ปฏิเสธการเข้า')
    repository = AccessRepository(store)
    repository.add_denied_access(event)
    return event


def process_access_scan(store: AccessStore, member_id: str, scan_method: str) -> dict:
    """FR-ACC-01, FR-ACC-02, FR-ACC-03, FR-ACC-05, FR-ACC-06: ตรวจไอดีภายนอก สอบสิทธิ์ และบันทึก access event เมื่ออนุญาตหรือปฏิเสธด้วยเหตุผลชัดเจน"""

    repository = AccessRepository(store)

    if not member_id or not member_id.strip():
        raise AccessScanUnreadable('Scan input is required')
    if scan_method not in {'qr', 'card'}:
        raise AccessScanUnreadable('Unsupported scan method')

    normalized = member_id.strip()
    if not verify_external_member_id(normalized):
        _record_denied_event(store, normalized, scan_method, 'not_found')
        raise AccessDenied('not_found', DENIAL_MESSAGES['not_found'])

    profile = find_member(normalized)
    if profile is None:
        _record_denied_event(store, normalized, scan_method, 'not_found')
        raise AccessDenied('not_found', DENIAL_MESSAGES['not_found'])

    reason_code = access_status_for_member(normalized)
    if reason_code == 'not_found':
        _record_denied_event(store, normalized, scan_method, 'not_found')
        raise AccessDenied('not_found', DENIAL_MESSAGES['not_found'])
    if reason_code == 'no_eligibility':
        _record_denied_event(store, normalized, scan_method, 'no_eligibility')
        raise AccessDenied('no_eligibility', DENIAL_MESSAGES['no_eligibility'])
    if reason_code == 'verification_failed':
        _record_denied_event(store, normalized, scan_method, 'verification_failed')
        raise AccessDenied('verification_failed', DENIAL_MESSAGES['verification_failed'])
    if not is_eligible_for_access(normalized):
        _record_denied_event(store, normalized, scan_method, 'no_eligibility')
        raise AccessDenied('no_eligibility', DENIAL_MESSAGES['no_eligibility'])

    event = AccessEvent.create(normalized, scan_method)
    event.member_id = normalized
    event.result_status = 'approved'

    current_occupancy = repository.add_successful_access(event)

    return {
        'status': 'approved',
        'allowed': True,
        'message': 'ยืนยันตัวตนสำเร็จ',
        'eventId': event.access_event_id,
        'memberId': normalized,
        'memberName': profile.name,
        'scannedAt': event.scanned_at,
        'currentOccupancy': current_occupancy,
    }
