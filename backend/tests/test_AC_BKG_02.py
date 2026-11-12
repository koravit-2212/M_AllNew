from datetime import date

from fastapi.testclient import TestClient

from app.api.spaces import get_space_store
from app.main import app
from app.models.space import build_seed_space_store

# test จาก specs/004-reserve/test-cases.md (AC-BKG-02) ห้ามแก้ให้ผ่าน

DAY = date(2026, 11, 13)


def _setup():
    store = build_seed_space_store(DAY)
    app.dependency_overrides[get_space_store] = lambda: store
    return store, TestClient(app)


def _body(slot):
    return {'spaceId': slot.space_id, 'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time}


def test_TC_BKG_02_1_book_free_slot_success():
    # Given ช่วงเวลา 09.00–11.00 น. ของพื้นที่หนึ่งว่าง และผู้จองเป็นนักศึกษา
    store, client = _setup()
    space = next(s for s in store.spaces if s.is_open)
    slot = next(s for s in store.slots_for(space.space_id) if s.start_time == '09:00')
    try:
        check = client.post('/api/reservations/check-availability', json=_body(slot))

        # When นักศึกษายืนยันการจอง
        created = client.post('/api/reservations', json={**_body(slot), 'userId': '64000001'})
        detail = client.get(f"/api/reservations/{created.json()['reservationId']}").json()
    finally:
        app.dependency_overrides.clear()

    # Then (1) ตรวจความว่างได้ผลว่าง
    assert check.json()['available'] is True
    # (2) บันทึกการจอง 1 รายการ ผู้จอง พื้นที่ ช่วงเวลาตรง และอ่านกลับมาได้
    assert len(store.reservations) == 1
    r = store.reservations[0]
    assert (r.user_id, r.space_id, r.slot_id) == ('64000001', space.space_id, slot.slot_id)
    assert detail['slotInfo'] == {'date': slot.date, 'startTime': '09:00', 'endTime': '11:00'}
    assert detail['spaceInfo']['facilityName'] == space.facility_name
    # (3) แจ้งผล "จองสำเร็จ"
    assert created.status_code == 201
    assert created.json()['message'] == 'จองสำเร็จ'
    # (4) หน้าจอ ตรวจด้วย vitest TC-BKG-02-1.test.jsx


def test_TC_BKG_02_2_last_free_slot_then_full():
    # Given พื้นที่หนึ่งเหลือช่วงว่างแค่ 1 ช่วง
    store, client = _setup()
    space = next(s for s in store.spaces if s.is_open)
    slots = store.slots_for(space.space_id)
    try:
        for slot in slots[:-1]:
            assert client.post('/api/reservations', json={**_body(slot), 'userId': '64000001'}).status_code == 201

        # When นักศึกษายืนยันการจองช่วงสุดท้าย
        last = client.post('/api/reservations', json={**_body(slots[-1]), 'userId': 'ST-1001'})
        listing = client.get('/api/spaces/available').json()['spaces']
    finally:
        app.dependency_overrides.clear()

    # Then (1) จองสำเร็จ
    assert last.status_code == 201
    # (2) พื้นที่นั้นขึ้นเต็ม
    assert next(s for s in listing if s['space_id'] == space.space_id)['available'] is False


def test_TC_BKG_02_3_ineligible_user_rejected():
    # Given ช่วงเวลาว่าง แต่ผู้จองไม่ใช่นักศึกษา บุคลากร หรือผู้ได้รับอนุญาต
    store, client = _setup()
    slot = store.slots_for(next(s for s in store.spaces if s.is_open).space_id)[0]
    try:
        # When ผู้ใช้นั้นยืนยันการจอง
        response = client.post('/api/reservations', json={**_body(slot), 'userId': 'GU-0001'})
        check = client.post('/api/reservations/check-availability', json=_body(slot)).json()
    finally:
        app.dependency_overrides.clear()

    # Then (1) ปฏิเสธพร้อมข้อความ "ไม่มีสิทธิ์จองพื้นที่"
    assert response.status_code == 403
    assert response.json()['detail'] == 'ไม่มีสิทธิ์จองพื้นที่'
    # (2) ไม่มีรายการจอง และช่วงเวลายังว่าง
    assert store.reservations == []
    assert check['available'] is True
    # (3) หน้าจอ ตรวจด้วย vitest TC-BKG-02-3.test.jsx
