from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.main import app
from app.models.equipment import build_seed_equipment_store


# T-09 (FR-EQP-02, FR-EQP-05) ตรวจด้วย AC-EQP-03

def test_AC_EQP_03_out_of_stock_message():
    # Given อุปกรณ์ที่ต้องการหมด
    store = build_seed_equipment_store()
    equipment = next(iter(store.equipment_types.values()))
    equipment.available_count = 0
    student = next(s for s in store.students.values() if not s.has_outstanding)
    app.dependency_overrides[get_equipment_store] = lambda: store
    try:
        client = TestClient(app)

        # When นักศึกษาขอยืมอุปกรณ์
        response = client.post(
            '/api/loan-requests',
            json={'student_id': student.student_id, 'equipment_type_id': equipment.equipment_type_id, 'quantity': 1},
        )
    finally:
        app.dependency_overrides.clear()

    # Then ระบบแจ้งว่าไม่สามารถยืมได้ และไม่สร้างคำขอใหม่
    assert response.status_code == 409
    assert response.json()['detail'] == 'ไม่สามารถยืมได้'
    assert store.requests == {}
    assert equipment.available_count == 0


def test_AC_EQP_03_request_more_than_available_is_rejected():
    store = build_seed_equipment_store()
    equipment = next(e for e in store.equipment_types.values() if e.available_count >= 1)
    student = next(s for s in store.students.values() if not s.has_outstanding)
    app.dependency_overrides[get_equipment_store] = lambda: store
    try:
        response = TestClient(app).post(
            '/api/loan-requests',
            json={
                'student_id': student.student_id,
                'equipment_type_id': equipment.equipment_type_id,
                'quantity': equipment.available_count + 1,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert store.requests == {}
