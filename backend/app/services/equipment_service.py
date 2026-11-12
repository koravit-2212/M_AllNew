from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import EQUIPMENT_LOAN_DAYS, LIBRARY_TIMEZONE
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


class StudentBlocked(Exception):
    """นักศึกษามีรายการค้างคืน การอนุมัติปกติถูกบล็อก ต้อง override (ASM-02, Q-04)"""


class InsufficientStock(Exception):
    """จำนวนคงเหลือไม่พอ ตอนส่งคำขอหรือตอนอนุมัติ (FR-EQP-02, FR-EQP-05)"""


def create_loan_request(store: EquipmentStore, student_id: str, equipment_type_id: str, quantity: int) -> LoanRequest:
    """FR-EQP-02, ASM-01: สร้างคำขอยืมสถานะรออนุมัติ ยังไม่ลดจำนวนคงเหลือ เพราะต้องผ่านเจ้าหน้าที่เสมอ
    FR-EQP-05: ถ้าจำนวนคงเหลือไม่พอ ปฏิเสธทันที ไม่สร้างคำขอ
    """

    with store.lock:
        if equipment_type_id not in store.equipment_types:
            raise EquipmentNotFound(equipment_type_id)
        if student_id not in store.students:
            raise StudentNotFound(student_id)
        if store.equipment_types[equipment_type_id].available_count < quantity:
            raise InsufficientStock(equipment_type_id)

        request_id = f'REQ-{len(store.requests) + 1:04d}'
        request = LoanRequest(
            request_id=request_id,
            student_id=student_id,
            equipment_type_id=equipment_type_id,
            quantity=quantity,
        )
        store.requests[request_id] = request
        return request


def library_today() -> date:
    """FR-EQP-04: วันที่ปัจจุบันตามเขตเวลาของห้องสมุด"""

    return datetime.now(ZoneInfo(LIBRARY_TIMEZONE)).date()


def compute_due_date(equipment_type_id: str, loan_date: date) -> date:
    """FR-EQP-04, ASM-03, Q-03, CON-LNS-02: กำหนดคืนตามประเภทอุปกรณ์ = วันที่ยืม + จำนวนวันใน config"""

    return loan_date + timedelta(days=EQUIPMENT_LOAN_DAYS[equipment_type_id])


def list_pending_requests(store: EquipmentStore) -> list[LoanRequest]:
    """FR-EQP-03: คำขอที่รอเจ้าหน้าที่ตรวจสอบ (หน้าจอเจ้าหน้าที่ตาม plan.md ข้อ 4 Pending requests list)"""

    return [request for request in store.requests.values() if request.status == 'pending']


def get_request_detail(store: EquipmentStore, request_id: str, today: date | None = None) -> dict:
    """FR-EQP-03, FR-EQP-06, CON-LNS-02: ข้อมูลที่เจ้าหน้าที่ใช้ตรวจก่อนอนุมัติ คือนักศึกษา อุปกรณ์ และรายการค้างคืน
    คำขอของนักศึกษาที่มีรายการค้างคืนยังเป็น pending ไม่อนุมัติเอง ให้เจ้าหน้าที่ตรวจก่อนตัดสินใจ (FR-EQP-06)
    `blocked` บอกว่าอนุมัติปกติไม่ได้ ต้อง override (ASM-02, Q-04)
    """

    request = store.requests.get(request_id)
    if request is None:
        raise RequestNotFound(request_id)
    student = store.students[request.student_id]
    equipment = store.equipment_types[request.equipment_type_id]
    # FR-EQP-04: กำหนดคืนถ้าอนุมัติวันนี้ ให้เจ้าหน้าที่เห็นก่อนอนุมัติ (UI-EQP-02)
    due_date = compute_due_date(equipment.equipment_type_id, today or library_today())
    return {
        'request_id': request.request_id,
        'status': request.status,
        'quantity': request.quantity,
        'student': {'student_id': student.student_id, 'name': student.name},
        'has_outstanding': student.has_outstanding,
        'blocked': student.has_outstanding,
        'outstanding_items': [dict(item) for item in student.outstanding_items],
        'equipment': {
            'equipment_type_id': equipment.equipment_type_id,
            'name': equipment.name,
            'available_count': equipment.available_count,
        },
        'due_date': due_date.isoformat(),
    }


def approve_request(
    store: EquipmentStore,
    request_id: str,
    approver_id: str,
    today: date | None = None,
    override: bool = False,
) -> LoanRecord:
    """FR-EQP-04, CON-LNS-02: เจ้าหน้าที่อนุมัติ ระบบบันทึกการยืมและลดจำนวนคงเหลือ
    ตรวจจำนวนอีกครั้งภายใต้ lock เพื่อไม่ให้คงเหลือติดลบ (FR-EQP-02)
    กำหนด due date ตามประเภทอุปกรณ์ (ASM-03, Q-03)
    FR-EQP-06, ASM-02, Q-04: นักศึกษาที่มีรายการค้างคืนถูกบล็อก เว้นแต่เจ้าหน้าที่ override (ไม่บังคับเหตุผล)
    """

    with store.lock:
        request = store.requests.get(request_id)
        if request is None:
            raise RequestNotFound(request_id)
        if request.status != 'pending':
            raise RequestNotPending(request_id)
        if store.students[request.student_id].has_outstanding and not override:
            raise StudentBlocked(request.student_id)
        equipment = store.equipment_types[request.equipment_type_id]
        if equipment.available_count < request.quantity:
            raise InsufficientStock(request.equipment_type_id)

        loan_date = today or library_today()
        equipment.available_count -= request.quantity
        request.status = 'approved'
        loan = LoanRecord(
            loan_id=f'LOAN-{len(store.loans) + 1:04d}',
            request_id=request.request_id,
            student_id=request.student_id,
            equipment_type_id=request.equipment_type_id,
            quantity=request.quantity,
            approved_by=approver_id,
            loan_date=loan_date,
            due_date=compute_due_date(request.equipment_type_id, loan_date),
        )
        store.loans.append(loan)
        return loan
