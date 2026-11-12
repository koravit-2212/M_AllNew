from datetime import date

from fastapi.testclient import TestClient

from app.api.spaces import get_space_store
from app.config import SPACE_SLOT_TIMES
from app.main import app
from app.models.space import build_seed_space_store
from app.services.reservation_service import SlotNotFound, create_reservation

# test จาก specs/004-reserve/test-cases.md (AC-BKG-01) ห้ามแก้ให้ผ่าน

DAY = date(2026, 11, 13)


def _get_spaces(store):
    app.dependency_overrides[get_space_store] = lambda: store
    try:
        return TestClient(app).get('/api/spaces/available').json()['spaces']
    finally:
        app.dependency_overrides.clear()


def test_TC_BKG_01_1_list_open_spaces_with_slots():
    # Given มีพื้นที่เปิดให้บริการ 3 แห่ง แต่ละแห่งมีช่วงเวลา 4 ช่วงที่ยังไม่มีใครจอง
    store = build_seed_space_store(DAY)
    open_ids = {s.space_id for s in store.spaces if s.is_open}
    assert len(open_ids) == 3 and len(SPACE_SLOT_TIMES) == 4

    # When นักศึกษาเลือกบริการพื้นที่
    spaces = _get_spaces(store)

    # Then (1) คืนพื้นที่เปิดให้บริการครบ 3 แห่ง แต่ละแห่งมีช่วงเวลา 4 ช่วงที่ว่าง
    assert {s['space_id'] for s in spaces} == open_ids
    for space in spaces:
        assert len(space['slots']) == 4
        assert all(slot['available'] for slot in space['slots'])
        # (2) ทุกแห่งมีชื่อและสถานะว่าง (การแสดงผลตรวจด้วย vitest TC-BKG-01-1.test.jsx)
        assert space['facility_name']
        assert space['available'] is True


def test_TC_BKG_01_2_fully_booked_space_marked_full():
    # Given พื้นที่ 1 แห่งถูกจองครบทุกช่วงเวลา ส่วนพื้นที่อื่นว่างทุกช่วง
    store = build_seed_space_store(DAY)
    full_id = next(s.space_id for s in store.spaces if s.is_open)
    for slot in store.slots_for(full_id):
        create_reservation(store, '64000001', full_id, slot.date, slot.start_time, slot.end_time)

    # When นักศึกษาเลือกบริการพื้นที่
    spaces = _get_spaces(store)

    # Then (1) พื้นที่ที่ว่าง 0 ช่วงขึ้นเต็ม และพื้นที่อื่นขึ้นว่าง
    full = next(s for s in spaces if s['space_id'] == full_id)
    assert full['available'] is False
    assert not any(slot['available'] for slot in full['slots'])
    assert all(s['available'] for s in spaces if s['space_id'] != full_id)
    # (2) การเลือกไม่ได้บนหน้าจอ ตรวจด้วย vitest TC-BKG-01-2.test.jsx


def test_TC_BKG_01_3_closed_space_not_listed():
    # Given มีพื้นที่ 1 แห่งที่ปิดให้บริการ
    store = build_seed_space_store(DAY)
    closed = next(s for s in store.spaces if not s.is_open)
    closed_slot = store.slots_for(closed.space_id)[0]

    # When นักศึกษาเลือกบริการพื้นที่
    spaces = _get_spaces(store)

    # Then (1) พื้นที่ที่ปิดไม่อยู่ในรายการ
    assert closed.space_id not in {s['space_id'] for s in spaces}
    # (2) จองพื้นที่ที่ปิดไม่ได้ และไม่มีรายการจองเกิดขึ้น
    try:
        create_reservation(store, '64000001', closed.space_id, closed_slot.date, closed_slot.start_time, closed_slot.end_time)
        booked = True
    except SlotNotFound:
        booked = False
    assert booked is False
    assert store.reservations == []
