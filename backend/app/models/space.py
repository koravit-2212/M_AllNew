from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.config import SPACE_BOOKING_TIMEZONE, SPACE_SEED_DATA, SPACE_SLOT_TIMES


@dataclass
class Space:
    """รองรับ FR-BKG-01, ASM-01: พื้นที่ที่ห้องสมุดกำหนดไว้ล่วงหน้า"""

    space_id: str
    space_type: str
    facility_name: str
    capacity: int
    status: str

    @property
    def is_open(self) -> bool:
        return self.status == 'open'


@dataclass
class SpaceTimeSlot:
    """รองรับ FR-BKG-01, FR-BKG-02: ช่วงเวลาของพื้นที่ 1 แห่งใน 1 วัน"""

    slot_id: str
    space_id: str
    date: str
    start_time: str
    end_time: str


@dataclass
class Reservation:
    """รองรับ FR-BKG-03: รายการจองที่บันทึกแล้ว"""

    reservation_id: str
    user_id: str
    space_id: str
    slot_id: str
    reservation_time: str
    status: str = 'confirmed'


def today_in_library_timezone() -> date:
    """glossary "วันเดียวกัน" เทียบด้วย Asia/Bangkok"""

    return datetime.now(ZoneInfo(SPACE_BOOKING_TIMEZONE)).date()


def build_slot_id(space_id: str, day: str, start_time: str) -> str:
    return f'{space_id}@{day}T{start_time}'


@dataclass
class SpaceStore:
    """รองรับ FR-BKG-01 ถึง FR-BKG-04, CON-CONC-01

    เก็บพื้นที่ ช่วงเวลา และการจองในหน่วยความจำ (ทีมเลือกเอง ไม่ได้มาจาก spec ใช้แนวทางเดียวกับ 003)
    `lock` ใช้ครอบการตรวจความว่างและบันทึกการจองให้เป็น atomic operation ตาม CON-CONC-01
    """

    spaces: list[Space] = field(default_factory=list)
    slots: list[SpaceTimeSlot] = field(default_factory=list)
    reservations: list[Reservation] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def get_space(self, space_id: str) -> Space | None:
        return next((space for space in self.spaces if space.space_id == space_id), None)

    def slots_for(self, space_id: str) -> list[SpaceTimeSlot]:
        return [slot for slot in self.slots if slot.space_id == space_id]


def build_seed_space_store(day: date | None = None) -> SpaceStore:
    """FR-BKG-01, ASM-01: สร้างพื้นที่และช่วงเวลาตัวอย่างของวันที่กำหนด (ค่าเริ่มต้นคือวันนี้ตามเวลา Asia/Bangkok)"""

    target_day = (day or today_in_library_timezone()).isoformat()
    spaces = [Space(**payload) for payload in SPACE_SEED_DATA]
    slots = [
        SpaceTimeSlot(
            slot_id=build_slot_id(space.space_id, target_day, start),
            space_id=space.space_id,
            date=target_day,
            start_time=start,
            end_time=end,
        )
        for space in spaces
        for start, end in SPACE_SLOT_TIMES
    ]
    return SpaceStore(spaces=spaces, slots=slots)
