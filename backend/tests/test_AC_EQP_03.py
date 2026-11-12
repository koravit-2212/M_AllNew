from conftest import create_request

# test จาก specs/007-equipment/test-cases.md (AC-EQP-03) ห้ามแก้ให้ผ่าน


def test_TC_EQP_03_1_out_of_stock_not_allowed(eqp_client, eqp_store, student_clear, type_id):
    # Given ถุงผ้าคงเหลือ 0 และนักศึกษาไม่มีรายการค้างคืน
    bag = type_id('ถุงผ้า')
    eqp_store.equipment_types[bag].available_count = 0

    # When นักศึกษาขอยืมถุงผ้า 1 ชิ้น
    response = create_request(eqp_client, student_clear.student_id, bag)

    # Then (1) API ตอบว่า "ไม่สามารถยืมได้"
    assert response.status_code == 409
    assert response.json()['detail'] == 'ไม่สามารถยืมได้'
    # (2) ไม่มีคำขอใหม่ถูกสร้าง
    assert eqp_store.requests == {}
    # (3) การแสดงผลบนหน้าจอ ตรวจด้วย vitest TC-EQP-03-1.test.jsx


def test_TC_EQP_03_2_request_equal_and_over_stock(eqp_client, eqp_store, student_clear, type_id):
    # Given ร่มคงเหลือ 1
    umbrella = type_id('ร่ม')
    eqp_store.equipment_types[umbrella].available_count = 1

    # When นักศึกษาขอยืมร่ม 1 ชิ้น แล้วขอยืมร่ม 2 ชิ้น
    one = create_request(eqp_client, student_clear.student_id, umbrella, quantity=1)
    two = create_request(eqp_client, student_clear.student_id, umbrella, quantity=2)

    # Then (1) คำขอ 1 ชิ้นสำเร็จ สถานะรออนุมัติ
    assert one.status_code == 201
    assert one.json()['status'] == 'pending'
    # (2) คำขอ 2 ชิ้นได้คำตอบว่า "ไม่สามารถยืมได้"
    assert two.status_code == 409
    assert two.json()['detail'] == 'ไม่สามารถยืมได้'
    # (3) มีคำขอที่ถูกสร้างแค่ 1 คำขอ
    assert len(eqp_store.requests) == 1


def test_TC_EQP_03_3_in_stock_no_message(eqp_client, eqp_store, student_clear, type_id):
    # Given ปลั๊กไฟคงเหลือ 4 ซึ่งไม่หมด
    plug = type_id('ปลั๊กไฟ')
    assert eqp_store.equipment_types[plug].available_count == 4

    # When นักศึกษาเลือกปลั๊กไฟ แล้วส่งคำขอยืม
    response = create_request(eqp_client, student_clear.student_id, plug)

    # Then (1) ไม่ได้รับข้อความ "ไม่สามารถยืมได้" (การแสดงบนหน้าจอตรวจด้วย vitest TC-EQP-03-3.test.jsx)
    assert 'ไม่สามารถยืมได้' not in response.text
    # (2) ส่งคำขอได้ สถานะรออนุมัติ
    assert response.status_code == 201
    assert response.json()['status'] == 'pending'
