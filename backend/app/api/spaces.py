from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.space import SpaceStore, build_seed_space_store

# FR-BKG-01, FR-BKG-02
# Route แสดงพื้นที่ที่ใช้งานได้พร้อมช่วงเวลา เก็บข้อมูลในหน่วยความจำแบบเดียวกับ 003 (ทีมเลือกเอง ไม่ได้มาจาก spec)

router = APIRouter(prefix='/api')

_store = build_seed_space_store()


def get_space_store() -> SpaceStore:
    """FR-BKG-01: ที่เก็บพื้นที่ที่ใช้ร่วมทุก route (test แทนที่ได้ด้วย dependency_overrides)"""

    return _store


def slot_is_available(store: SpaceStore, slot_id: str) -> bool:
    """FR-BKG-02: ช่วงเวลาว่างเมื่อยังไม่มีการจองที่ยืนยันแล้วในช่วงนั้น"""

    return not any(r.slot_id == slot_id and r.status == 'confirmed' for r in store.reservations)


@router.get('/spaces/available')
def list_available_spaces(
    day: str | None = Query(None, alias='date', description='วันที่ YYYY-MM-DD (ไม่ระบุ = ทุกวันที่มีในระบบ)'),
    store: SpaceStore = Depends(get_space_store),
) -> dict:
    """FR-BKG-01: พื้นที่ที่เปิดให้บริการ พร้อมช่วงเวลาและสถานะว่างของแต่ละช่วง (พื้นที่ที่ปิดไม่แสดง)"""

    if day is not None:
        try:
            date.fromisoformat(day)
        except ValueError:
            raise HTTPException(status_code=422, detail='Invalid date')

    spaces = []
    for space in store.spaces:
        if not space.is_open:
            continue
        slots = [
            {
                'slot_id': slot.slot_id,
                'date': slot.date,
                'start_time': slot.start_time,
                'end_time': slot.end_time,
                'available': slot_is_available(store, slot.slot_id),
            }
            for slot in store.slots_for(space.space_id)
            if day is None or slot.date == day
        ]
        spaces.append(
            {
                'space_id': space.space_id,
                'space_type': space.space_type,
                'facility_name': space.facility_name,
                'available': any(slot['available'] for slot in slots),
                'slots': slots,
            }
        )
    return {'spaces': spaces}
