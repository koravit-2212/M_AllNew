from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models.access_event import AccessEvent
from app.models.facility_occupancy import AccessStore, build_seed_access_store
from app.services.access_service import AccessDenied, AccessScanUnreadable, process_access_scan
from app.services.external_id_service import ExternalIdentityVerificationError
from app.services.manual_verification_service import create_manual_verification_audit

# FR-ACC-01, FR-ACC-03, CON-IDN-01, CON-SEC-01
# Route ของการยืนยันตัวตนและบันทึก access log ให้เริ่มต้นในรูปแบบ contract ที่พร้อมต่อเฟสถัดไป

router = APIRouter(prefix='/api')
_store = build_seed_access_store()


def get_access_store() -> AccessStore:
    """FR-ACC-03: store ที่ใช้ร่วมกันบน route ของการสแกนเข้าห้องสมุด"""

    return _store


class ScanIn(BaseModel):
    scanMethod: str = Field(default='qr')
    qrCodeOrCardId: str = Field(min_length=1)


class VerifyManualIn(BaseModel):
    eventId: str = Field(min_length=1)
    staffId: str = Field(min_length=1)
    reason: str = ''
    manualApproved: bool = True


@router.post('/access/scan')
def scan_access(body: ScanIn, store: AccessStore = Depends(get_access_store)) -> dict:
    """FR-ACC-01, FR-ACC-02, FR-ACC-03: ตรวจข้อมูลภายนอกและสิทธิ์ แล้วบันทึก event เมื่ออนุญาตให้เข้า"""

    if body.scanMethod not in {'qr', 'card'}:
        raise HTTPException(status_code=422, detail='Unsupported scan method')
    if not body.qrCodeOrCardId or body.qrCodeOrCardId == '':
        raise HTTPException(status_code=422, detail='Scan input is required')

    try:
        return process_access_scan(store, body.qrCodeOrCardId, body.scanMethod)
    except AccessDenied as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except AccessScanUnreadable as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExternalIdentityVerificationError as exc:
        raise HTTPException(status_code=404, detail=f'ไม่พบข้อมูล {exc}') from exc


@router.get('/access/status')
def access_status(store: AccessStore = Depends(get_access_store)) -> dict:
    """FR-ACC-03: คืนจำนวนผู้ใช้บริการปัจจุบันและเวลาปรับปรุงล่าสุด"""

    with store.lock:
        occupancy = store.occupancy
        return {
            'currentOccupancy': occupancy.current_occupancy,
            'lastUpdatedAt': occupancy.updated_at,
        }


@router.post('/access/verify-manual')
def verify_access_manually(
    body: VerifyManualIn,
    store: AccessStore = Depends(get_access_store),
) -> dict:
    """FR-ACC-06: รับสิทธิ์จากเจ้าหน้าที่ที่มีสิทธิ์และบันทึก audit log (contract ประเภทอ่าน/ยืนยันด้วยมือ)"""

    event = next((item for item in store.events if item.access_event_id == body.eventId), None)
    if event is None:
        raise HTTPException(status_code=404, detail='Event not found')

    audit = create_manual_verification_audit(event, body.staffId, body.reason, body.manualApproved)
    approved = audit.approved_by_staff
    if approved:
        with store.lock:
            store.occupancy.current_occupancy += 1
            store.occupancy.refresh_timestamp()
        message = 'ยืนยันตัวตนด้วยมือสำเร็จ'
    else:
        message = 'ปฏิเสธการเข้า โดยเจ้าหน้าที่ยืนยันว่าควรปฏิเสธ'

    return {
        'auditId': audit.audit_id,
        'approved': approved,
        'message': message,
    }
