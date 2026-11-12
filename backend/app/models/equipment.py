from __future__ import annotations

import threading
from dataclasses import dataclass, field

from app.config import EQUIPMENT_SEED_DATA, EQUIPMENT_STUDENT_SEED_DATA


@dataclass
class EquipmentType:
    """รองรับ FR-EQP-01, FR-EQP-02: ประเภทอุปกรณ์และจำนวนคงเหลือ"""

    equipment_type_id: str
    name: str
    available_count: int


@dataclass
class Student:
    """รองรับ FR-EQP-03, FR-EQP-06, CON-LNS-02: ข้อมูลนักศึกษาที่เจ้าหน้าที่ใช้ตรวจ รวมรายการค้างคืน"""

    student_id: str
    name: str
    outstanding_items: list[dict] = field(default_factory=list)

    @property
    def has_outstanding(self) -> bool:
        return bool(self.outstanding_items)


@dataclass
class LoanRequest:
    """รองรับ FR-EQP-02, FR-EQP-03, ASM-01: คำขอยืมที่รอเจ้าหน้าที่อนุมัติ"""

    request_id: str
    student_id: str
    equipment_type_id: str
    quantity: int
    status: str = 'pending'


@dataclass
class LoanRecord:
    """รองรับ FR-EQP-04: การยืมที่บันทึกหลังเจ้าหน้าที่อนุมัติ (due date รอ T-13)"""

    loan_id: str
    request_id: str
    student_id: str
    equipment_type_id: str
    quantity: int
    approved_by: str


@dataclass
class EquipmentStore:
    """รองรับ FR-EQP-01 ถึง FR-EQP-06: ที่เก็บอุปกรณ์ นักศึกษา คำขอ และการยืมในหน่วยความจำ (แนวทางเดียวกับ 003)

    `lock` ใช้ครอบการตรวจจำนวนคงเหลือกับการลดจำนวน เพื่อไม่ให้จำนวนติดลบเมื่ออนุมัติพร้อมกัน
    """

    equipment_types: dict[str, EquipmentType] = field(default_factory=dict)
    students: dict[str, Student] = field(default_factory=dict)
    requests: dict[str, LoanRequest] = field(default_factory=dict)
    loans: list[LoanRecord] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)


def build_seed_equipment_store() -> EquipmentStore:
    """FR-EQP-01, FR-EQP-03: สร้างที่เก็บเริ่มต้นจากข้อมูลตัวอย่างใน config"""

    equipment_types = {payload['equipment_type_id']: EquipmentType(**payload) for payload in EQUIPMENT_SEED_DATA}
    students = {
        payload['student_id']: Student(
            student_id=payload['student_id'],
            name=payload['name'],
            outstanding_items=[dict(item) for item in payload['outstanding_items']],
        )
        for payload in EQUIPMENT_STUDENT_SEED_DATA
    }
    return EquipmentStore(equipment_types=equipment_types, students=students)
