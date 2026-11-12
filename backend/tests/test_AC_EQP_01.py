# test จาก specs/007-equipment/test-cases.md (AC-EQP-01) ห้ามแก้ให้ผ่าน


def test_TC_EQP_01_1_show_all_types_selectable(eqp_client, eqp_store):
    # Given ระบบมีอุปกรณ์ 3 ประเภท คือ ปลั๊กไฟ ร่ม ถุงผ้า และทุกประเภทมีคงเหลือมากกว่า 0
    assert all(e.available_count > 0 for e in eqp_store.equipment_types.values())

    # When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
    response = eqp_client.get('/api/equipment-types')

    # Then (1) API คืนครบทั้ง 3 ประเภท พร้อมจำนวนคงเหลือของแต่ละประเภท
    assert response.status_code == 200
    items = response.json()['items']
    assert {item['name'] for item in items} == {'ปลั๊กไฟ', 'ร่ม', 'ถุงผ้า'}
    for item in items:
        assert item['available_count'] == eqp_store.equipment_types[item['equipment_type_id']].available_count
    # (2)(3) การแสดงผลและการเลือกตรวจด้วย vitest TC-EQP-01-1.test.jsx


def test_TC_EQP_01_2_zero_stock_type_in_list(eqp_client, eqp_store, type_id):
    # Given ประเภทหนึ่งมีคงเหลือ 0 อีก 2 ประเภทคงเหลือ 1 ขึ้นไป
    zero_id = type_id('ถุงผ้า')
    eqp_store.equipment_types[zero_id].available_count = 0

    # When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
    items = eqp_client.get('/api/equipment-types').json()['items']

    # Then (1) ประเภทที่คงเหลือ 1 ขึ้นไปอยู่ในรายการให้เลือก
    in_stock = [item for item in items if item['equipment_type_id'] != zero_id]
    assert len(in_stock) == 2
    assert all(item['available_count'] >= 1 for item in in_stock)
    # (2) ประเภทที่คงเหลือ 0 อยู่ในรายการ พร้อมจำนวน 0 เพื่อให้หน้าจอระบุว่าหมด (Q-06)
    zero = [item for item in items if item['equipment_type_id'] == zero_id]
    assert len(zero) == 1
    assert zero[0]['available_count'] == 0
    # (3) การแจ้ง "ไม่สามารถยืมได้" เมื่อเลือก ตรวจด้วย vitest TC-EQP-01-2.test.jsx


def test_TC_EQP_01_3_no_equipment_in_system(eqp_client, eqp_store):
    # Given ระบบไม่มีรายการอุปกรณ์ให้บริการเลย
    eqp_store.equipment_types.clear()

    # When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
    response = eqp_client.get('/api/equipment-types')

    # Then (1) API คืนรายการว่าง
    assert response.status_code == 200
    assert response.json()['items'] == []
    # (2) หน้าจอแสดงรายการว่างและส่งคำขอไม่ได้ ตรวจด้วย vitest TC-EQP-01-3.test.jsx
