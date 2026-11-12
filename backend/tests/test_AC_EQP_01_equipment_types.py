from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.config import EQUIPMENT_SEED_DATA
from app.main import app
from app.models.equipment import build_seed_equipment_store


# T-03 (FR-EQP-01, FR-EQP-02) ตรวจด้วย AC-EQP-01

def test_AC_EQP_01_show_equipment_types():
    # Given มีรายการอุปกรณ์ให้บริการในระบบ
    store = build_seed_equipment_store()
    app.dependency_overrides[get_equipment_store] = lambda: store
    try:
        client = TestClient(app)

        # When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
        response = client.get('/api/equipment-types')
    finally:
        app.dependency_overrides.clear()

    # Then ระบบแสดงประเภทอุปกรณ์ที่สามารถยืมได้ให้เลือก พร้อมจำนวนคงเหลือ
    assert response.status_code == 200
    items = response.json()['items']
    expected = {seed['equipment_type_id']: seed for seed in EQUIPMENT_SEED_DATA}
    assert {item['equipment_type_id'] for item in items} == set(expected)
    for item in items:
        assert item['name'] == expected[item['equipment_type_id']]['name']
        assert item['available_count'] == expected[item['equipment_type_id']]['available_count']
    assert {item['name'] for item in items} == {'ปลั๊กไฟ', 'ร่ม', 'ถุงผ้า'}
