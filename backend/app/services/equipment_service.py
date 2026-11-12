from __future__ import annotations

from app.models.equipment import EquipmentStore, LoanRequest

# FR-EQP-02, FR-EQP-03, FR-EQP-04, ASM-01
# กฎของบริการยืมอุปกรณ์ แยกจาก route เพื่อให้ test เรียกได้ตรง ๆ


class EquipmentNotFound(Exception):
    """ไม่พบประเภทอุปกรณ์ที่ขอยืม"""


class StudentNotFound(Exception):
    """ไม่พบนักศึกษาที่ส่งคำขอ"""


def create_loan_request(store: EquipmentStore, student_id: str, equipment_type_id: str, quantity: int) -> LoanRequest:
    """FR-EQP-02, ASM-01: สร้างคำขอยืมสถานะรออนุมัติ ยังไม่ลดจำนวนคงเหลือ เพราะต้องผ่านเจ้าหน้าที่เสมอ"""

    with store.lock:
        if equipment_type_id not in store.equipment_types:
            raise EquipmentNotFound(equipment_type_id)
        if student_id not in store.students:
            raise StudentNotFound(student_id)

        request_id = f'REQ-{len(store.requests) + 1:04d}'
        request = LoanRequest(
            request_id=request_id,
            student_id=student_id,
            equipment_type_id=equipment_type_id,
            quantity=quantity,
        )
        store.requests[request_id] = request
        return request
