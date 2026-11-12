from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.main import app
from app.models.equipment import build_seed_equipment_store


# T-14 (FR-EQP-06, ASM-02, Q-04) ตรวจด้วย AC-EQP-04

def _setup(with_outstanding: bool):
    store = build_seed_equipment_store()
    student = next(s for s in store.students.values() if s.has_outstanding == with_outstanding)
    equipment = next(e for e in store.equipment_types.values() if e.available_count >= 1)
    app.dependency_overrides[get_equipment_store] = lambda: store
    client = TestClient(app)
    request_id = client.post(
        '/api/loan-requests',
        json={'student_id': student.student_id, 'equipment_type_id': equipment.equipment_type_id},
    ).json()['request_id']
    return store, client, equipment, request_id


def test_AC_EQP_04_block_and_override():
    # Given นักศึกษามีรายการค้างคืน
    # When นักศึกษาขอยืมอุปกรณ์เพิ่ม
    store, client, equipment, request_id = _setup(with_outstanding=True)
    before = equipment.available_count
    try:
        detail = client.get(f'/api/loan-requests/{request_id}').json()

        # Then อนุมัติแบบปกติถูกบล็อก (ASM-02)
        blocked = client.post(f'/api/loan-requests/{request_id}/approve')

        # เจ้าหน้าที่ตรวจรายการค้างคืนแล้วตัดสินใจปลดล็อกเป็นกรณีพิเศษ (override ไม่ต้องใส่เหตุผล Q-04)
        overridden = client.post(f'/api/loan-requests/{request_id}/override')
    finally:
        app.dependency_overrides.clear()

    assert detail['blocked'] is True
    assert blocked.status_code == 409
    assert blocked.json()['detail'] == 'มีรายการค้างคืน'

    assert overridden.status_code == 200
    assert overridden.json()['override'] is True
    assert overridden.json()['available_count'] == before - 1
    assert len(store.loans) == 1
    assert store.requests[request_id].status == 'approved'


def test_AC_EQP_04_blocked_approve_changes_nothing():
    store, client, equipment, request_id = _setup(with_outstanding=True)
    before = equipment.available_count
    try:
        client.post(f'/api/loan-requests/{request_id}/approve')
    finally:
        app.dependency_overrides.clear()

    assert equipment.available_count == before
    assert store.loans == []
    assert store.requests[request_id].status == 'pending'


def test_AC_EQP_04_student_without_outstanding_not_blocked():
    store, client, equipment, request_id = _setup(with_outstanding=False)
    try:
        detail = client.get(f'/api/loan-requests/{request_id}').json()
        approved = client.post(f'/api/loan-requests/{request_id}/approve')
    finally:
        app.dependency_overrides.clear()

    assert detail['blocked'] is False
    assert approved.status_code == 200
    assert approved.json()['override'] is False
