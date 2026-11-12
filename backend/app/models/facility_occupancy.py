from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.models.access_event import AccessEvent


@dataclass
class FacilityOccupancy:
    """FR-ACC-03: จำนวนผู้ใช้บริการปัจจุบันในอาคารพร้อมเวลาปรับปรุงล่าสุดเพื่อแสดงบน kiosk"""

    facility_id: str = 'library-main'
    current_occupancy: int = 128
    updated_at: str = ''

    def refresh_timestamp(self) -> None:
        """FR-ACC-03: อัปเดต timestamp หลังเปลี่ยนสถานะการเข้า/ออกของผู้ใช้บริการ"""

        self.updated_at = datetime.now(UTC).isoformat(timespec='seconds')


@dataclass
class AccessStore:
    """FR-ACC-03, NFR-PRF-01, NFR-PRF-02: เก็บ access log และ current occupancy แบบ thread-safe เพื่อรองรับ concurrent requests"""

    events: list[AccessEvent] = field(default_factory=list)
    occupancy: FacilityOccupancy = field(default_factory=FacilityOccupancy)
    lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def add_event(self, event: AccessEvent) -> None:
        """FR-ACC-03: บันทึก event ใหม่ก่อน route อื่นจะอ่านข้อมูลต่อ"""

        self.events.append(event)

    def increment_occupancy(self, delta: int = 1) -> int:
        """NFR-PRF-01, NFR-PRF-02: อัปเดต current_occupancy แบบ atomic ภายใต้ shared lock เพื่อหลีกเลี่ยง race condition"""

        with self.lock:
            self.occupancy.current_occupancy += delta
            self.occupancy.refresh_timestamp()
            return self.occupancy.current_occupancy


def build_seed_access_store() -> AccessStore:
    """FR-ACC-03: สร้าง store ตัวอย่างสำหรับการทดสอบและเริ่มต้นหน้า kiosk"""

    store = AccessStore()
    store.occupancy.refresh_timestamp()
    return store
