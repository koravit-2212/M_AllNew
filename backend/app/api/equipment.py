from fastapi import APIRouter, Depends

from app.models.equipment import EquipmentStore, build_seed_equipment_store

# FR-EQP-01, FR-EQP-02
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
