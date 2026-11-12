from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.config import EQUIPMENT_LOAN_DAYS
from app.main import app
from app.models.equipment import build_seed_equipment_store
from app.services.equipment_service import approve_request, create_loan_request, get_request_detail, library_today


# T-13 (FR-EQP-04, ASM-03, Q-03, CON-LNS-02) ตรวจด้วย AC-EQP-02

def test_AC_EQP_02_due_date_per_equipment_type():
    # Given อุปกรณ์มีพอและนักศึกษาไม่มีรายการค้างคืน ทุกประเภทอุปกรณ์
    store = build_seed_equipment_store()
    student = next(s for s in store.students.values() if not s.has_outstanding)
    loan_date = date(2026, 11, 12)

    for equipment in store.equipment_types.values():
        request = create_loan_request(store, student.student_id, equipment.equipment_type_id, 1)
        expected = loan_date + timedelta(days=EQUIPMENT_LOAN_DAYS[equipment.equipment_type_id])

        # เจ้าหน้าที่เห็นกำหนดคืนก่อนอนุมัติ
        assert get_request_detail(store, request.request_id, today=loan_date)['due_date'] == expected.isoformat()

        # When เจ้าหน้าที่อนุมัติการยืม
        loan = approve_request(store, request.request_id, '', today=loan_date)

        # Then ระบบบันทึกการยืมพร้อม due date ตามประเภทอุปกรณ์
        assert loan.loan_date == loan_date
        assert loan.due_date == expected


def test_AC_EQP_02_every_seed_type_has_loan_days_of_one_day():
    # Q-03: ทีมตอบว่าทุกประเภท 1 วัน
    store = build_seed_equipment_store()
    assert set(EQUIPMENT_LOAN_DAYS) == set(store.equipment_types)
    assert all(days == 1 for days in EQUIPMENT_LOAN_DAYS.values())


def test_AC_EQP_02_approve_api_returns_due_date():
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
        detail = client.get(f'/api/loan-requests/{request_id}').json()
        approved = client.post(f'/api/loan-requests/{request_id}/approve').json()
    finally:
        app.dependency_overrides.clear()

    expected = (library_today() + timedelta(days=EQUIPMENT_LOAN_DAYS[equipment.equipment_type_id])).isoformat()
    assert detail['due_date'] == expected
    assert approved['due_date'] == expected
    assert store.loans[0].due_date.isoformat() == expected
