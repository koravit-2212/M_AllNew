from fastapi.testclient import TestClient
import pytest

from app.api.access import get_access_store
from app.main import app
from app.models.facility_occupancy import build_seed_access_store
from app.services.access_service import AccessDenied, process_access_scan


def test_T06_access_denial_classifies_reasons_and_records_event():
    # Given นักศึกษาที่ไม่มีสิทธิ์และนักศึกษาที่ไม่สามารถตรวจสอบสิทธิ์ได้
    no_eligibility_store = build_seed_access_store()
    verification_failed_store = build_seed_access_store()
    not_found_store = build_seed_access_store()

    # When ระบบประมวลผล scan เพื่อปฏิเสธตามสาเหตุที่แตกต่างกัน
    with pytest.raises(AccessDenied, match='ไม่มีสิทธิ์'):
        process_access_scan(no_eligibility_store, 'STD-1002', 'qr')
    with pytest.raises(AccessDenied, match='ไม่สามารถตรวจสอบสิทธิ์ได้'):
        process_access_scan(verification_failed_store, 'STD-1003', 'qr')
    with pytest.raises(AccessDenied, match='ไม่พบข้อมูล'):
        process_access_scan(not_found_store, 'UNKNOWN-999', 'qr')

    # Then event จะถูกบันทึกด้วย reason code ที่ชัดเจน และมี flag สำหรับ manual verification
    assert no_eligibility_store.events[-1].result_status == 'no_eligibility'
    assert no_eligibility_store.events[-1].manual_verification_required is True
    assert verification_failed_store.events[-1].result_status == 'verification_failed'
    assert verification_failed_store.events[-1].manual_verification_required is True
    assert not_found_store.events[-1].result_status == 'not_found'
    assert not_found_store.events[-1].manual_verification_required is True


def test_T06_manual_verification_audit_is_recorded_for_staff_decision():
    # Given event ที่ปฏิเสธด้วยเหตุผลต่าง ๆ
    store = build_seed_access_store()
    app.dependency_overrides[get_access_store] = lambda: store
    try:
        response = TestClient(app).post('/api/access/scan', json={'scanMethod': 'qr', 'qrCodeOrCardId': 'STD-1002'})
        assert response.status_code == 403
        event_id = store.events[-1].access_event_id

        # When เจ้าหน้าที่ยืนยันด้วยมือให้อนุญาตให้เข้าได้
        audit_response = TestClient(app).post('/api/access/verify-manual', json={
            'eventId': event_id,
            'staffId': 'STAFF-01',
            'reason': 'ตรวจสอบเอกสารยืนยันสิทธิ์แล้ว',
            'manualApproved': True,
        })
    finally:
        app.dependency_overrides.clear()

    # Then ระบบต้องบันทึก audit log และปรับสถานะเป็น approved_manual
    assert audit_response.status_code == 200
    payload = audit_response.json()
    assert payload['approved'] is True
    assert payload['message'] == 'ยืนยันตัวตนด้วยมือสำเร็จ'
    assert payload['auditId'] == f'audit-{event_id}'
    assert store.events[-1].result_status == 'approved_manual'
