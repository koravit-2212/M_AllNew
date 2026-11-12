from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import SPACE_BOOKING_TIMEZONE, SPACE_ELIGIBLE_USER_TYPES, SPACE_USER_SEED_DATA
from app.models.space import Reservation, SpaceStore, SpaceTimeSlot

# FR-BKG-02, FR-BKG-03, FR-BKG-04, CON-ELG-01, CON-CONC-01
# กฎการจองพื้นที่ แยกจาก route เพื่อให้ test เรียกได้ตรง ๆ


class UserNotEligible(Exception):
    """ผู้ใช้ไม่มีสิทธิ์จองพื้นที่ (CON-ELG-01)"""


class SlotNotFound(Exception):
    """ไม่พบพื้นที่หรือช่วงเวลาที่เลือก หรือพื้นที่ปิดให้บริการ"""


class SlotUnavailable(Exception):
    """พื้นที่ไม่ว่างในช่วงเวลานั้น (FR-BKG-04)"""


def find_user(user_id: str) -> dict | None:
    """CON-ELG-01, Q-01: หาผู้ใช้ตัวอย่างจาก config (ชั่วคราวจนกว่าจะมี 001/002)"""

    return next((user for user in SPACE_USER_SEED_DATA if user['user_id'] == user_id), None)


def is_eligible(user_id: str) -> bool:
    """CON-ELG-01: ผู้จองต้องเป็นนักศึกษา บุคลากร หรือผู้ได้รับอนุญาต"""

    user = find_user(user_id)
    return user is not None and user['user_type'] in SPACE_ELIGIBLE_USER_TYPES


def find_slot(store: SpaceStore, space_id: str, day: str, start_time: str, end_time: str) -> SpaceTimeSlot:
    """FR-BKG-02: หาช่วงเวลาของพื้นที่ที่เปิดให้บริการ"""

    space = store.get_space(space_id)
    if space is None or not space.is_open:
        raise SlotNotFound(space_id)
    for slot in store.slots_for(space_id):
        if slot.date == day and slot.start_time == start_time and slot.end_time == end_time:
            return slot
    raise SlotNotFound(f'{space_id}@{day}T{start_time}-{end_time}')


def _slot_taken(store: SpaceStore, slot_id: str) -> bool:
    return any(r.slot_id == slot_id and r.status == 'confirmed' for r in store.reservations)


def check_availability(store: SpaceStore, space_id: str, day: str, start_time: str, end_time: str) -> dict:
    """FR-BKG-02: ตรวจความว่างของพื้นที่ตามช่วงเวลาที่เลือก"""

    slot = find_slot(store, space_id, day, start_time, end_time)
    if _slot_taken(store, slot.slot_id):
        return {'available': False, 'reason': 'พื้นที่ไม่ว่างในช่วงเวลานี้'}
    return {'available': True, 'reason': ''}


def create_reservation(
    store: SpaceStore, user_id: str, space_id: str, day: str, start_time: str, end_time: str
) -> Reservation:
    """FR-BKG-02, FR-BKG-03, CON-CONC-01: ตรวจความว่างและบันทึกการจองภายใต้ lock เดียวกัน (atomic)
    CON-ELG-01: ตรวจสิทธิ์ผู้จองก่อน
    FR-BKG-04: ช่วงที่ถูกจองแล้ว ปฏิเสธโดยไม่สร้างรายการซ้อน
    """

    if not is_eligible(user_id):
        raise UserNotEligible(user_id)
    with store.lock:
        slot = find_slot(store, space_id, day, start_time, end_time)
        if _slot_taken(store, slot.slot_id):
            raise SlotUnavailable(slot.slot_id)
        reservation = Reservation(
            reservation_id=f'RSV-{len(store.reservations) + 1:04d}',
            user_id=user_id,
            space_id=space_id,
            slot_id=slot.slot_id,
            reservation_time=datetime.now(ZoneInfo(SPACE_BOOKING_TIMEZONE)).isoformat(timespec='seconds'),
        )
        store.reservations.append(reservation)
        return reservation


def get_reservation(store: SpaceStore, reservation_id: str) -> Reservation | None:
    """FR-BKG-03: อ่านการจองที่บันทึกแล้ว"""

    return next((r for r in store.reservations if r.reservation_id == reservation_id), None)
