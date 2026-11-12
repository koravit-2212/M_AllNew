from datetime import date

from fastapi.testclient import TestClient

from app.api.spaces import get_space_store
from app.main import app
from app.models.space import build_seed_space_store

# test จาก specs/004-reserve/test-cases.md (AC-BKG-03) ห้ามแก้ให้ผ่าน

DAY = date(2026, 11, 13)


def _body(slot, user_id):
    return {'userId': user_id, 'spaceId': slot.space_id, 'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time}


def _slot(store, space_id, start):
    return next(s for s in store.slots_for(space_id) if s.start_time == start)


def test_TC_BKG_03_1_booked_slot_rejected_no_duplicate():
    # Given ช่วง 11.00–13.00 น. ของพื้นที่หนึ่งถูกจองไปแล้ว 1 รายการ
    store = build_seed_space_store(DAY)
    space_id = next(s.space_id for s in store.spaces if s.is_open)
    slot = _slot(store, space_id, '11:00')
    app.dependency_overrides[get_space_store] = lambda: store
    try:
        client = TestClient(app)
        assert client.post('/api/reservations', json=_body(slot, '64000001')).status_code == 201

        # When นักศึกษาอีกคนพยายามจองพื้นที่และช่วงเวลาเดียวกัน
        response = client.post('/api/reservations', json=_body(slot, 'ST-1001'))
    finally:
        app.dependency_overrides.clear()

    # Then (1) แจ้ง "พื้นที่ไม่ว่างในช่วงเวลานี้"
    assert response.status_code == 409
    assert response.json()['detail'] == 'พื้นที่ไม่ว่างในช่วงเวลานี้'
    # (2) รายการจองของช่วงนั้นยังเป็น 1
    assert [r.slot_id for r in store.reservations].count(slot.slot_id) == 1
    # (3) หน้าจอ ตรวจด้วย vitest TC-BKG-03-1.test.jsx


def test_TC_BKG_03_2_adjacent_slot_and_other_space_ok():
    # Given ช่วง 09.00–11.00 น. ของพื้นที่ A ถูกจองแล้ว
    store = build_seed_space_store(DAY)
    a, b = [s.space_id for s in store.spaces if s.is_open][:2]
    app.dependency_overrides[get_space_store] = lambda: store
    try:
        client = TestClient(app)
        assert client.post('/api/reservations', json=_body(_slot(store, a, '09:00'), '64000001')).status_code == 201

        # When จองช่วง 11.00–13.00 น. ของพื้นที่ A และช่วง 09.00–11.00 น. ของพื้นที่ B
        r1 = client.post('/api/reservations', json=_body(_slot(store, a, '11:00'), 'ST-1001'))
        r2 = client.post('/api/reservations', json=_body(_slot(store, b, '09:00'), 'ST-1001'))
    finally:
        app.dependency_overrides.clear()

    # Then (1) จองทั้ง 2 รายการสำเร็จ
    assert (r1.status_code, r2.status_code) == (201, 201)
    # (2) มีการจองรวม 3 รายการ ไม่มีช่วงใดถูกจองซ้ำ
    slot_ids = [r.slot_id for r in store.reservations]
    assert len(slot_ids) == 3
    assert len(set(slot_ids)) == 3


def test_TC_BKG_03_3_free_slot_not_rejected():
    # Given พื้นที่ที่เลือกว่างในช่วงเวลานั้น
    store = build_seed_space_store(DAY)
    slot = _slot(store, next(s.space_id for s in store.spaces if s.is_open), '13:00')
    app.dependency_overrides[get_space_store] = lambda: store
    try:
        # When นักศึกษาพยายามจอง
        response = TestClient(app).post('/api/reservations', json=_body(slot, '64000001'))
    finally:
        app.dependency_overrides.clear()

    # Then (1) ไม่มีข้อความพื้นที่ไม่ว่าง
    assert 'พื้นที่ไม่ว่างในช่วงเวลานี้' not in response.text
    # (2) จองสำเร็จ
    assert response.status_code == 201
