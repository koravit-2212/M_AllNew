from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.main import app
from app.models.equipment import build_seed_equipment_store


# T-06 (FR-EQP-03, FR-EQP-04, CON-LNS-02) ตรวจด้วย AC-EQP-02

def _setup():
    store = build_seed_equipment_store()
    app.dependency_overrides[get_equipment_store] = lambda: store
    student = next(s for s in store.students.values() if not s.has_outstanding)
    equipment = next(e for e in store.equipment_types.values() if e.available_count >= 1)
    return store, TestClient(app), student, equipment


def test_AC_EQP_02_approve_and_record():
    store, client, student, equipment = _setup()
    try:
        # Given อุปกรณ์ที่ต้องการมีจำนวนเพียงพอและนักศึกษาไม่มีรายการค้างคืน
        before = equipment.available_count
        created = client.post(
            '/api/loan-requests',
            json={'student_id': student.student_id, 'equipment_type_id': equipment.equipment_type_id, 'quantity': 1},
        ).json()

        # เจ้าหน้าที่ตรวจข้อมูลนักศึกษาและรายการค้างคืนก่อน (FR-EQP-03)
        detail = client.get(f"/api/loan-requests/{created['request_id']}").json()
        assert detail['student']['student_id'] == student.student_id
        assert detail['student']['name'] == student.name
        assert detail['equipment']['name'] == equipment.name
        assert detail['quantity'] == 1
        assert detail['outstanding_items'] == []

        pending = client.get('/api/loan-requests').json()['items']
        assert [item['request_id'] for item in pending] == [created['request_id']]

        # When เจ้าหน้าที่อนุมัติการยืม
        response = client.post(f"/api/loan-requests/{created['request_id']}/approve", json={})
    finally:
        app.dependency_overrides.clear()

    # Then ระบบบันทึกการยืมและลดจำนวนอุปกรณ์คงเหลือ
    assert response.status_code == 200
    payload = response.json()
    assert payload['available_count'] == before - 1
    assert equipment.available_count == before - 1
    assert len(store.loans) == 1
    assert store.loans[0].student_id == student.student_id
    assert store.loans[0].equipment_type_id == equipment.equipment_type_id
    assert store.requests[created['request_id']].status == 'approved'


def test_AC_EQP_02_approve_twice_does_not_reduce_stock_again():
    store, client, student, equipment = _setup()
    try:
        before = equipment.available_count
        created = client.post(
            '/api/loan-requests',
            json={'student_id': student.student_id, 'equipment_type_id': equipment.equipment_type_id},
        ).json()
        first = client.post(f"/api/loan-requests/{created['request_id']}/approve")
        second = client.post(f"/api/loan-requests/{created['request_id']}/approve")
        missing = client.get('/api/loan-requests/REQ-9999')
    finally:
        app.dependency_overrides.clear()

    assert first.status_code == 200
    assert second.status_code == 409
    assert missing.status_code == 404
    assert equipment.available_count == before - 1
    assert len(store.loans) == 1
