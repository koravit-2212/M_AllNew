from datetime import date

from fastapi.testclient import TestClient

from app.api.spaces import get_space_store
from app.config import SPACE_SLOT_TIMES
from app.main import app
from app.models.space import Reservation, build_seed_space_store


# T-03 (FR-BKG-01) ตรวจด้วย AC-BKG-01

def test_AC_BKG_01_display_available_spaces():
    # Given มีพื้นที่เปิดให้บริการในระบบ และมี 1 ช่วงเวลาถูกจองแล้ว
    store = build_seed_space_store(date(2026, 11, 13))
    open_ids = {s.space_id for s in store.spaces if s.is_open}
    booked = store.slots_for(sorted(open_ids)[0])[0]
    store.reservations.append(Reservation('R-1', 'u', booked.space_id, booked.slot_id, 'now'))
    app.dependency_overrides[get_space_store] = lambda: store
    try:
        # When นักศึกษาเลือกบริการพื้นที่
        response = TestClient(app).get('/api/spaces/available', params={'date': '2026-11-13'})
    finally:
        app.dependency_overrides.clear()

    # Then ระบบแสดงรายการพื้นที่ที่ใช้งานได้พร้อมช่วงเวลาให้เลือก
    assert response.status_code == 200
    spaces = response.json()['spaces']
    assert {s['space_id'] for s in spaces} == open_ids
    for space in spaces:
        assert space['facility_name']
        assert len(space['slots']) == len(SPACE_SLOT_TIMES)
    slots = {slot['slot_id']: slot for s in spaces for slot in s['slots']}
    assert slots[booked.slot_id]['available'] is False
    assert sum(1 for slot in slots.values() if not slot['available']) == 1


def test_AC_BKG_01_space_full_when_all_slots_booked():
    store = build_seed_space_store(date(2026, 11, 13))
    space_id = next(s.space_id for s in store.spaces if s.is_open)
    for i, slot in enumerate(store.slots_for(space_id)):
        store.reservations.append(Reservation(f'R-{i}', 'u', space_id, slot.slot_id, 'now'))
    app.dependency_overrides[get_space_store] = lambda: store
    try:
        spaces = TestClient(app).get('/api/spaces/available').json()['spaces']
    finally:
        app.dependency_overrides.clear()

    full = next(s for s in spaces if s['space_id'] == space_id)
    assert full['available'] is False
    assert all(s['available'] for s in spaces if s['space_id'] != space_id)
