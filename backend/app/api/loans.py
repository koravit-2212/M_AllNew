from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.repositories.loan_repository import LoanRepository
from app.services.loan_service import LoanService
from app.services.member_profile_seed import find_loan_member, loan_history_for_member

# FR-LNS-01, FR-LNS-02, FR-LNS-03, FR-LNS-05, FR-LNS-06, FR-LNS-07
# route นี้รวม logic ยืมจริงและคืนจริงตาม contract ของ feature นี้

router = APIRouter(prefix='/api')
_loan_repository = LoanRepository()
_loan_service = LoanService(_loan_repository)


class BorrowRequest(BaseModel):
    member_id: str
    barcode: str
    source: str = 'counter'


class ReturnRequest(BaseModel):
    member_id: str
    barcode: str


@router.post('/loans/borrow')
def borrow_book(payload: BorrowRequest) -> dict:
    """FR-LNS-01, FR-LNS-02, FR-LNS-03: ตรวจสิทธิ์ก่อนบันทึกการยืมและตั้ง notification ให้ล่วงหน้า 1–3 วัน"""

    member_id = (payload.member_id or '').strip()
    barcode = (payload.barcode or '').strip()
    if not member_id:
        raise HTTPException(status_code=400, detail='member_id is required')
    if not barcode:
        raise HTTPException(status_code=400, detail='barcode is required')

    member = find_loan_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail='member_not_found')

    copy = _loan_repository.copy_for_barcode(barcode)
    if copy is None:
        raise HTTPException(status_code=404, detail='copy_not_found')

    result = _loan_service.borrow_book(member_id, copy.copy_id, source=payload.source)
    if not result['allowed']:
        return JSONResponse(
            status_code=400,
            content={'status': result['status'], 'message': result['message']},
        )
    return result


@router.post('/loans/return')
def return_book(payload: ReturnRequest) -> dict:
    """FR-LNS-05, FR-LNS-06: บันทึกการคืน, คำนวณ overdue_days และ penalty_amount, และบันทึก audit log ได้จริง"""

    member_id = (payload.member_id or '').strip()
    barcode = (payload.barcode or '').strip()
    if not member_id:
        raise HTTPException(status_code=400, detail='member_id is required')
    if not barcode:
        raise HTTPException(status_code=400, detail='barcode is required')

    member = find_loan_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail='member_not_found')

    copy = _loan_repository.copy_for_barcode(barcode)
    if copy is None:
        raise HTTPException(status_code=404, detail='copy_not_found')

    result = _loan_service.return_book(member_id, copy.copy_id)
    if not result['allowed']:
        return JSONResponse(
            status_code=400,
            content={'status': result['status'], 'message': result['message']},
        )
    return result


@router.get('/loans/history/{member_id}')
def loan_history(member_id: str) -> dict:
    """FR-LNS-07: ส่งประวัติการยืม-คืนที่ได้จาก repository แบบ real data ของสมาชิกที่ร้องขอ"""

    member = find_loan_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail='member_not_found')

    return {
        'member_id': member_id,
        'history': _loan_service.member_history(member_id),
    }
