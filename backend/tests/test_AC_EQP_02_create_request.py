from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.main import app
from app.models.equipment import build_seed_equipment_store


# T-05 (FR-EQP-02, ASM-01) ตรวจด้วย AC-EQP-02 (ส่วนส่งคำขอก่อนเจ้าหน้าที่อนุมัติ)

def _client_with(store):
    app.dependency_overrides[get_equipment_store] = lambda: store
    return TestClient(app)


def _student_without_outstanding(store):
    return next(s for s in store.students.values() if not s.has_outstanding)


def test_AC_EQP_02_create_request_is_pending_and_stock_unchanged():
    # Given อุปกรณ์ที่ต้องการมีจำนวนเพียงพอและนักศึกษาไม่มีรายการค้างคืน
    store = build_seed_equipment_store()
    equipment = next(e for e in store.equipment_types.values() if e.available_count >= 1)
    before = equipment.available_count
    student = _student_without_outstanding(store)
    try:
        client = _client_with(store)

        # When นักศึกษาส่งคำขอยืม
        response = client.post(
            '/api/loan-requests',
            json={'student_id': student.student_id, 'equipment_type_id': equipment.equipment_type_id, 'quantity': 1},
        )
    finally:
        app.dependency_overrides.clear()

    # Then ได้คำขอสถานะรออนุมัติ และจำนวนคงเหลือยังไม่ลด (ASM-01 ต้องผ่านเจ้าหน้าที่เสมอ)
    assert response.status_code == 201
    payload = response.json()
    assert payload['status'] == 'pending'
    assert payload['request_id'] in store.requests
    assert equipment.available_count == before
    assert store.loans == []


def test_AC_EQP_02_create_request_unknown_student_or_equipment_returns_404():
    store = build_seed_equipment_store()
    student = _student_without_outstanding(store)
    equipment_id = next(iter(store.equipment_types))
    try:
        client = _client_with(store)
        r1 = client.post('/api/loan-requests', json={'student_id': 'nobody', 'equipment_type_id': equipment_id})
        r2 = client.post('/api/loan-requests', json={'student_id': student.student_id, 'equipment_type_id': 'nothing'})
    finally:
        app.dependency_overrides.clear()

    assert r1.status_code == 404
    assert r2.status_code == 404
    assert store.requests == {}


def test_AC_EQP_02_list_students_for_selection():
    store = build_seed_equipment_store()
    try:
        response = _client_with(store).get('/api/students')
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    ids = {item['student_id'] for item in response.json()['items']}
    assert ids == set(store.students)
