from datetime import date

from fastapi.testclient import TestClient

from app.api.spaces import get_space_store
from app.main import app
from app.models.space import build_seed_space_store


# T-07 (FR-BKG-02, FR-BKG-04, CON-CONC-01) ตรวจด้วย AC-BKG-03

def test_AC_BKG_03_unavailable_space_rejected():
    # Given พื้นที่ที่เลือกไม่ว่างในช่วงเวลานั้น (มีผู้จองไปแล้ว)
    store = build_seed_space_store(date(2026, 11, 13))
    app.dependency_overrides[get_space_store] = lambda: store
    space = next(s for s in store.spaces if s.is_open)
    slot = store.slots_for(space.space_id)[1]
    body = {'spaceId': space.space_id, 'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time}
    try:
        client = TestClient(app)
        first = client.post('/api/reservations', json={**body, 'userId': '64000001'})
        count_before = len(store.reservations)

        # When นักศึกษาพยายามจอง
        check = client.post('/api/reservations/check-availability', json=body)
        second = client.post('/api/reservations', json={**body, 'userId': 'ST-1001'})
    finally:
        app.dependency_overrides.clear()

    # Then ระบบแจ้งให้เลือกพื้นที่หรือเวลาอื่น และไม่มีรายการจองซ้อนเกิดขึ้น
    assert first.status_code == 201
    assert check.json() == {'available': False, 'reason': 'พื้นที่ไม่ว่างในช่วงเวลานี้'}
    assert second.status_code == 409
    assert second.json()['detail'] == 'พื้นที่ไม่ว่างในช่วงเวลานี้'
    assert len(store.reservations) == count_before == 1
    assert [r.slot_id for r in store.reservations].count(slot.slot_id) == 1


def test_AC_BKG_03_other_slot_same_space_still_bookable():
    store = build_seed_space_store(date(2026, 11, 13))
    app.dependency_overrides[get_space_store] = lambda: store
    space = next(s for s in store.spaces if s.is_open)
    slot_a, slot_b = store.slots_for(space.space_id)[:2]
    try:
        client = TestClient(app)
        for slot in (slot_a, slot_b):
            r = client.post('/api/reservations', json={'userId': '64000001', 'spaceId': space.space_id, 'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time})
            assert r.status_code == 201
    finally:
        app.dependency_overrides.clear()

    assert len(store.reservations) == 2
