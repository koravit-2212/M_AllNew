from __future__ import annotations

from app.models.access_event import AccessEvent
from app.models.facility_occupancy import AccessStore


class AccessRepository:
    """FR-ACC-03, NFR-PRF-01, NFR-PRF-02: repository สำหรับจัดเก็บ access event และอัปเดต occupancy แบบ thread-safe"""

    def __init__(self, store: AccessStore):
        self.store = store

    def add_successful_access(self, event: AccessEvent) -> int:
        """NFR-PRF-01: เพิ่ม event และอัปเดต occupancy ภายใต้ lock เดียวกันเพื่อให้ request พร้อมกันไม่ชนกัน"""

        with self.store.lock:
            self.store.add_event(event)
            self.store.occupancy.current_occupancy += 1
            self.store.occupancy.refresh_timestamp()
            return self.store.occupancy.current_occupancy

    def add_denied_access(self, event: AccessEvent) -> None:
        """FR-ACC-05: บันทึก event ที่ปฏิเสธโดยไม่ปรับ occupancy เพื่อให้สถานะ "ไม่สามารถอ่านข้อมูล" และ "ไม่พบข้อมูล" เป็นอิสระ"""

        with self.store.lock:
            self.store.add_event(event)

    def current_occupancy(self) -> int:
        """FR-ACC-03: อ่านจำนวนผู้ใช้บริการปัจจุบันจาก store ที่มี lock ควบคุมความพร้อมใช้งาน"""

        with self.store.lock:
            return self.store.occupancy.current_occupancy
