from datetime import date

from app.config import SPACE_SLOT_TIMES
from app.models.space import build_seed_space_store


# T-01 (FR-BKG-01, CON-CONC-01, ASM-01) งานพื้นฐาน ไม่มี AC ตรง ๆ

def test_BKG_T01_seed_has_at_least_two_open_spaces_with_slots():
    store = build_seed_space_store(date(2026, 11, 13))

    open_spaces = [space for space in store.spaces if space.is_open]
    assert len(open_spaces) >= 2

    for space in open_spaces:
        slots = store.slots_for(space.space_id)
        assert len(slots) == len(SPACE_SLOT_TIMES)
        assert all(slot.date == '2026-11-13' for slot in slots)
        assert all(slot.start_time < slot.end_time for slot in slots)


def test_BKG_T01_slot_ids_are_unique_and_store_starts_without_reservations():
    store = build_seed_space_store(date(2026, 11, 13))

    slot_ids = [slot.slot_id for slot in store.slots]
    assert len(slot_ids) == len(set(slot_ids))
    assert store.reservations == []
    assert store.lock.acquire(blocking=False)
    store.lock.release()
