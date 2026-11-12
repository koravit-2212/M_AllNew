from datetime import date

from fastapi.testclient import TestClient

from app.api.spaces import get_space_store
from app.main import app
from app.models.space import build_seed_space_store


# T-05 (FR-BKG-02, FR-BKG-03, CON-CONC-01, CON-ELG-01) ตรวจด้วย AC-BKG-02

def _setup():
    store = build_seed_space_store(date(2026, 11, 13))
    app.dependency_overrides[get_space_store] = lambda: store
    space = next(s for s in store.spaces if s.is_open)
    slot = store.slots_for(space.space_id)[0]
    body = {'spaceId': space.space_id, 'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time}
    return store, TestClient(app), space, slot, body


def test_AC_BKG_02_successful_reservation():
    # Given มีพื้นที่ว่างในช่วงเวลาที่นักศึกษาเลือก
    store, client, space, slot, body = _setup()
    try:
        check = client.post('/api/reservations/check-availability', json=body)

        # When นักศึกษายืนยันการจอง
        created = client.post('/api/reservations', json={**body, 'userId': '64000001'})
        detail = client.get(f"/api/reservations/{created.json()['reservationId']}")
        listing = client.get('/api/spaces/available').json()['spaces']
    finally:
        app.dependency_overrides.clear()

    # Then ระบบตรวจสอบความว่างผ่าน บันทึกการจอง และแจ้งผลสำเร็จ
    assert check.json() == {'available': True, 'reason': ''}
    assert created.status_code == 201
    assert created.json()['status'] == 'confirmed'
    assert created.json()['message'] == 'จองสำเร็จ'
    assert len(store.reservations) == 1
    assert store.reservations[0].slot_id == slot.slot_id
    assert detail.json()['spaceInfo']['facilityName'] == space.facility_name
    assert detail.json()['slotInfo'] == {'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time}
    booked = next(s for sp in listing for s in sp['slots'] if s['slot_id'] == slot.slot_id)
    assert booked['available'] is False


def test_AC_BKG_02_not_eligible_user_rejected():
    # CON-ELG-01: ผู้ใช้ที่ไม่ใช่นักศึกษา บุคลากร หรือผู้ได้รับอนุญาต จองไม่ได้
    store, client, space, slot, body = _setup()
    try:
        guest = client.post('/api/reservations', json={**body, 'userId': 'GU-0001'})
        unknown = client.post('/api/reservations', json={**body, 'userId': 'nobody'})
        staff = client.post('/api/reservations', json={**body, 'userId': 'ST-1001'})
    finally:
        app.dependency_overrides.clear()

    assert guest.status_code == 403
    assert guest.json()['detail'] == 'ไม่มีสิทธิ์จองพื้นที่'
    assert unknown.status_code == 403
    assert staff.status_code == 201
    assert len(store.reservations) == 1


def test_AC_BKG_02_closed_space_or_unknown_slot_not_found():
    store, client, space, slot, body = _setup()
    closed = next(s for s in store.spaces if not s.is_open)
    try:
        r1 = client.post('/api/reservations', json={**body, 'spaceId': closed.space_id, 'userId': '64000001'})
        r2 = client.post('/api/reservations', json={**body, 'startTime': '23:00', 'userId': '64000001'})
    finally:
        app.dependency_overrides.clear()

    assert r1.status_code == 404
    assert r2.status_code == 404
    assert store.reservations == []
