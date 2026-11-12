from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.main import app
from app.models.equipment import build_seed_equipment_store


# T-11 (FR-EQP-03, FR-EQP-06, CON-LNS-02) ตรวจด้วย AC-EQP-04

def test_AC_EQP_04_outstanding_shown_to_staff_before_decision():
    # Given นักศึกษามีรายการค้างคืนอุปกรณ์หรือหนังสือ
    store = build_seed_equipment_store()
    student = next(s for s in store.students.values() if s.has_outstanding)
    equipment = next(e for e in store.equipment_types.values() if e.available_count >= 1)
    before = equipment.available_count
    app.dependency_overrides[get_equipment_store] = lambda: store
    try:
        client = TestClient(app)

        # When นักศึกษาขอยืมอุปกรณ์เพิ่ม
        created = client.post(
            '/api/loan-requests',
            json={'student_id': student.student_id, 'equipment_type_id': equipment.equipment_type_id, 'quantity': 1},
        )
        request_id = created.json()['request_id']
        detail = client.get(f'/api/loan-requests/{request_id}')
        pending = client.get('/api/loan-requests')
    finally:
        app.dependency_overrides.clear()

    # Then เจ้าหน้าที่ต้องตรวจสอบรายการค้างคืนก่อนตัดสินใจอนุมัติ
    # คำขอไม่ถูกอนุมัติเอง ยังรอเจ้าหน้าที่ และไม่มีการยืมหรือลดคงเหลือ
    assert created.status_code == 201
    assert created.json()['status'] == 'pending'
    assert store.loans == []
    assert equipment.available_count == before

    # เจ้าหน้าที่เห็นรายการค้างคืนในรายละเอียดคำขอ และในรายการคำขอที่รอตรวจ
    payload = detail.json()
    assert payload['has_outstanding'] is True
    assert payload['outstanding_items'] == student.outstanding_items
    pending_item = next(item for item in pending.json()['items'] if item['request_id'] == request_id)
    assert pending_item['outstanding_items'] == student.outstanding_items


def test_AC_EQP_04_student_without_outstanding_has_flag_false():
    store = build_seed_equipment_store()
    student = next(s for s in store.students.values() if not s.has_outstanding)
    equipment = next(e for e in store.equipment_types.values() if e.available_count >= 1)
    app.dependency_overrides[get_equipment_store] = lambda: store
    try:
        client = TestClient(app)
        request_id = client.post(
            '/api/loan-requests',
            json={'student_id': student.student_id, 'equipment_type_id': equipment.equipment_type_id},
        ).json()['request_id']
        payload = client.get(f'/api/loan-requests/{request_id}').json()
    finally:
        app.dependency_overrides.clear()

    assert payload['has_outstanding'] is False
    assert payload['outstanding_items'] == []
