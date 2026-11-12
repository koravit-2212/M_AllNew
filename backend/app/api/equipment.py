from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models.equipment import EquipmentStore, LoanRequest, build_seed_equipment_store
from app.services.equipment_service import EquipmentNotFound, StudentNotFound, create_loan_request

# FR-EQP-01, FR-EQP-02, FR-EQP-03, ASM-01
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
    """FR-EQP-02, ASM-01: นักศึกษาส่งคำขอยืม ได้คำขอสถานะ pending รอเจ้าหน้าที่"""

    try:
        request = create_loan_request(store, body.student_id, body.equipment_type_id, body.quantity)
    except EquipmentNotFound:
        raise HTTPException(status_code=404, detail='Equipment type not found')
    except StudentNotFound:
        raise HTTPException(status_code=404, detail='Student not found')
    return _request_payload(request)
