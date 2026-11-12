from __future__ import annotations

from app.models.equipment import EquipmentStore, LoanRecord, LoanRequest

# FR-EQP-02, FR-EQP-03, FR-EQP-04, ASM-01
# กฎของบริการยืมอุปกรณ์ แยกจาก route เพื่อให้ test เรียกได้ตรง ๆ


class EquipmentNotFound(Exception):
    """ไม่พบประเภทอุปกรณ์ที่ขอยืม"""


class StudentNotFound(Exception):
    """ไม่พบนักศึกษาที่ส่งคำขอ"""


class RequestNotFound(Exception):
    """ไม่พบคำขอยืม"""


class RequestNotPending(Exception):
    """คำขอนี้ไม่ได้อยู่ในสถานะรออนุมัติแล้ว"""


class InsufficientStock(Exception):
    """จำนวนคงเหลือไม่พอตอนอนุมัติ (FR-EQP-02)"""


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


def list_pending_requests(store: EquipmentStore) -> list[LoanRequest]:
    """FR-EQP-03: คำขอที่รอเจ้าหน้าที่ตรวจสอบ (หน้าจอเจ้าหน้าที่ตาม plan.md ข้อ 4 Pending requests list)"""

    return [request for request in store.requests.values() if request.status == 'pending']


def get_request_detail(store: EquipmentStore, request_id: str) -> dict:
    """FR-EQP-03, CON-LNS-02: ข้อมูลที่เจ้าหน้าที่ใช้ตรวจก่อนอนุมัติ คือนักศึกษา อุปกรณ์ และรายการค้างคืน"""

    request = store.requests.get(request_id)
    if request is None:
        raise RequestNotFound(request_id)
    student = store.students[request.student_id]
    equipment = store.equipment_types[request.equipment_type_id]
    return {
        'request_id': request.request_id,
        'status': request.status,
        'quantity': request.quantity,
        'student': {'student_id': student.student_id, 'name': student.name},
        'outstanding_items': [dict(item) for item in student.outstanding_items],
        'equipment': {
            'equipment_type_id': equipment.equipment_type_id,
            'name': equipment.name,
            'available_count': equipment.available_count,
        },
    }


def approve_request(store: EquipmentStore, request_id: str, approver_id: str) -> LoanRecord:
    """FR-EQP-04, CON-LNS-02: เจ้าหน้าที่อนุมัติ ระบบบันทึกการยืมและลดจำนวนคงเหลือ
    ตรวจจำนวนอีกครั้งภายใต้ lock เพื่อไม่ให้คงเหลือติดลบ (FR-EQP-02)
    due date ตามประเภทอุปกรณ์ยังไม่ทำ รอ T-13
    """

    with store.lock:
        request = store.requests.get(request_id)
        if request is None:
            raise RequestNotFound(request_id)
        if request.status != 'pending':
            raise RequestNotPending(request_id)
        equipment = store.equipment_types[request.equipment_type_id]
        if equipment.available_count < request.quantity:
            raise InsufficientStock(request.equipment_type_id)

        equipment.available_count -= request.quantity
        request.status = 'approved'
        loan = LoanRecord(
            loan_id=f'LOAN-{len(store.loans) + 1:04d}',
            request_id=request.request_id,
            student_id=request.student_id,
            equipment_type_id=request.equipment_type_id,
            quantity=request.quantity,
            approved_by=approver_id,
        )
        store.loans.append(loan)
        return loan
