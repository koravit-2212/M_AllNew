from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.spaces import get_space_store
from app.config import SPACE_USER_SEED_DATA
from app.models.space import SpaceStore
from app.services.reservation_service import (
    SlotNotFound,
    SlotUnavailable,
    UserNotEligible,
    check_availability,
    create_reservation,
    get_reservation,
)

# FR-BKG-02, FR-BKG-03, FR-BKG-04, CON-ELG-01, CON-CONC-01
# Route ตรวจความว่างและบันทึกการจองพื้นที่ (สัญญา API ตาม plan.md ข้อ 4 ใช้ชื่อฟิลด์ camelCase)

router = APIRouter(prefix='/api')


class SlotIn(BaseModel):
    spaceId: str
    date: str
    startTime: str
    endTime: str


class ReservationIn(SlotIn):
    userId: str = Field(min_length=1)


@router.get('/space-users')
def list_space_users() -> dict:
    """CON-ELG-01, Q-01: ผู้ใช้ตัวอย่างให้หน้าจองเลือก ชั่วคราวจนกว่าจะมีระบบยืนยันตัวตน"""

    return {'items': [{'userId': u['user_id'], 'name': u['name'], 'userType': u['user_type']} for u in SPACE_USER_SEED_DATA]}


@router.post('/reservations/check-availability')
def check_availability_endpoint(body: SlotIn, store: SpaceStore = Depends(get_space_store)) -> dict:
    """FR-BKG-02: ตรวจความว่างของพื้นที่ ณ ช่วงเวลาที่เลือก"""

    try:
        return check_availability(store, body.spaceId, body.date, body.startTime, body.endTime)
    except SlotNotFound:
        raise HTTPException(status_code=404, detail='Space or time slot not found')


@router.post('/reservations', status_code=201)
def create_reservation_endpoint(body: ReservationIn, store: SpaceStore = Depends(get_space_store)) -> dict:
    """FR-BKG-02, FR-BKG-03: ตรวจความว่างและบันทึกการจองแบบ atomic แล้วแจ้งผลสำเร็จ
    CON-ELG-01: ผู้ไม่มีสิทธิ์ตอบ 403
    """

    try:
        reservation = create_reservation(store, body.userId, body.spaceId, body.date, body.startTime, body.endTime)
    except UserNotEligible:
        raise HTTPException(status_code=403, detail='ไม่มีสิทธิ์จองพื้นที่')
    except SlotNotFound:
        raise HTTPException(status_code=404, detail='Space or time slot not found')
    except SlotUnavailable:
        raise HTTPException(status_code=409, detail='พื้นที่ไม่ว่างในช่วงเวลานี้')
    return {'reservationId': reservation.reservation_id, 'status': reservation.status, 'message': 'จองสำเร็จ'}


@router.get('/reservations/{reservation_id}')
def get_reservation_endpoint(reservation_id: str, store: SpaceStore = Depends(get_space_store)) -> dict:
    """FR-BKG-03: อ่านการจองที่บันทึกแล้ว พร้อมข้อมูลพื้นที่และช่วงเวลา"""

    reservation = get_reservation(store, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail='Reservation not found')
    space = store.get_space(reservation.space_id)
    slot = next(s for s in store.slots if s.slot_id == reservation.slot_id)
    return {
        'reservationId': reservation.reservation_id,
        'reservationStatus': reservation.status,
        'userId': reservation.user_id,
        'spaceInfo': {'spaceId': space.space_id, 'facilityName': space.facility_name},
        'slotInfo': {'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time},
    }
