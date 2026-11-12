from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models.equipment import EquipmentStore, LoanRequest, build_seed_equipment_store
from app.services.equipment_service import (
    EquipmentNotFound,
    InsufficientStock,
    RequestNotFound,
    RequestNotPending,
    StudentNotFound,
    approve_request,
    create_loan_request,
    get_request_detail,
    list_pending_requests,
)

# FR-EQP-01, FR-EQP-02, FR-EQP-03, FR-EQP-04, FR-EQP-05, FR-EQP-06, ASM-01
# Route ของบริการยืมอุปกรณ์ เก็บข้อมูลในหน่วยความจำแบบเดียวกับ 003 (ทีมเลือกเอง ไม่ได้มาจาก spec)

router = APIRouter(prefix='/api')

_store = build_seed_equipment_store()


def get_equipment_store() -> EquipmentStore:
    """FR-EQP-01, FR-EQP-02: ที่เก็บอุปกรณ์ที่ใช้ร่วมทุก route (test แทนที่ได้ด้วย dependency_overrides)"""

    return _store


@router.get('/equipment-types')
def list_equipment_types(store: EquipmentStore = Depends(get_equipment_store)) -> dict:
    """FR-EQP-01, FR-EQP-02: คืนประเภทอุปกรณ์ทั้งหมดให้นักศึกษาเลือก พร้อมจำนวนคงเหลือ"""

    return {
        'items': [
            {
                'equipment_type_id': item.equipment_type_id,
                'name': item.name,
                'available_count': item.available_count,
            }
            for item in store.equipment_types.values()
        ]
    }


@router.get('/students')
def list_students(store: EquipmentStore = Depends(get_equipment_store)) -> dict:
    """FR-EQP-03: รายชื่อนักศึกษาตัวอย่างให้หน้านักศึกษาเลือก
    ชั่วคราวจนกว่าจะมีระบบล็อกอิน (001/002) ตามที่ทีมตอบข้อเสนอคำถามข้อ 3 ใน tasks.md
    """

    return {
        'items': [{'student_id': student.student_id, 'name': student.name} for student in store.students.values()]
    }


class LoanRequestIn(BaseModel):
    student_id: str
    equipment_type_id: str
    quantity: int = Field(1, ge=1)


def _request_payload(request: LoanRequest) -> dict:
    return {
        'request_id': request.request_id,
        'student_id': request.student_id,
        'equipment_type_id': request.equipment_type_id,
        'quantity': request.quantity,
        'status': request.status,
    }


@router.post('/loan-requests', status_code=201)
def create_loan_request_endpoint(body: LoanRequestIn, store: EquipmentStore = Depends(get_equipment_store)) -> dict:
    """FR-EQP-02, ASM-01: นักศึกษาส่งคำขอยืม ได้คำขอสถานะ pending รอเจ้าหน้าที่
    FR-EQP-05: อุปกรณ์หมดหรือไม่พอ ตอบ 409 "ไม่สามารถยืมได้"
    """

    try:
        request = create_loan_request(store, body.student_id, body.equipment_type_id, body.quantity)
    except InsufficientStock:
        raise HTTPException(status_code=409, detail='ไม่สามารถยืมได้')
    except EquipmentNotFound:
        raise HTTPException(status_code=404, detail='Equipment type not found')
    except StudentNotFound:
        raise HTTPException(status_code=404, detail='Student not found')
    return _request_payload(request)


@router.get('/loan-requests')
def list_pending_requests_endpoint(store: EquipmentStore = Depends(get_equipment_store)) -> dict:
    """FR-EQP-03: รายการคำขอที่รอเจ้าหน้าที่ตรวจสอบ"""

    return {'items': [get_request_detail(store, request.request_id) for request in list_pending_requests(store)]}


@router.get('/loan-requests/{request_id}')
def get_loan_request_endpoint(request_id: str, store: EquipmentStore = Depends(get_equipment_store)) -> dict:
    """FR-EQP-03, FR-EQP-06, CON-LNS-02: รายละเอียดคำขอพร้อมรายการค้างคืนของนักศึกษา ให้เจ้าหน้าที่ตรวจก่อนตัดสินใจ"""

    try:
        return get_request_detail(store, request_id)
    except RequestNotFound:
        raise HTTPException(status_code=404, detail='Loan request not found')


class ApproveIn(BaseModel):
    # ยังไม่มีระบบล็อกอิน (001/002) จึงไม่บังคับรหัสเจ้าหน้าที่ ตามคำตอบทีมข้อ 3 (ชั่วคราว)
    approver_id: str = ''


@router.post('/loan-requests/{request_id}/approve')
def approve_loan_request_endpoint(
    request_id: str,
    body: ApproveIn | None = None,
    store: EquipmentStore = Depends(get_equipment_store),
) -> dict:
    """FR-EQP-03, FR-EQP-04: เจ้าหน้าที่อนุมัติ บันทึกการยืม และคืนจำนวนคงเหลือใหม่"""

    approver_id = body.approver_id if body else ''
    try:
        loan = approve_request(store, request_id, approver_id)
    except RequestNotFound:
        raise HTTPException(status_code=404, detail='Loan request not found')
    except RequestNotPending:
        raise HTTPException(status_code=409, detail='Loan request is not pending')
    except InsufficientStock:
        raise HTTPException(status_code=409, detail='ไม่สามารถยืมได้')

    equipment = store.equipment_types[loan.equipment_type_id]
    return {
        'loan_id': loan.loan_id,
        'request_id': loan.request_id,
        'student_id': loan.student_id,
        'equipment_type_id': loan.equipment_type_id,
        'equipment_name': equipment.name,
        'quantity': loan.quantity,
        'available_count': equipment.available_count,
    }
