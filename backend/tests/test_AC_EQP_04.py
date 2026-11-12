from datetime import date

from conftest import create_request

# test จาก specs/007-equipment/test-cases.md (AC-EQP-04) ห้ามแก้ให้ผ่าน


def test_TC_EQP_04_1_outstanding_shown_and_blocked(eqp_client, eqp_store, student_outstanding, type_id):
    # Given นักศึกษาค้างคืนร่ม เกินกำหนด 2 วัน และปลั๊กไฟคงเหลือ 4
    assert student_outstanding.outstanding_items == [{'item': 'ร่ม', 'days_overdue': 2}]
    plug = type_id('ปลั๊กไฟ')

    # When นักศึกษาขอยืมปลั๊กไฟ 1 ชิ้น แล้วเจ้าหน้าที่เปิดคำขอ
    created = create_request(eqp_client, student_outstanding.student_id, plug)
    request_id = created.json()['request_id']
    detail = eqp_client.get(f'/api/loan-requests/{request_id}').json()

    # Then (1) คำขอถูกสร้าง สถานะรออนุมัติ ไม่อนุมัติเอง
    assert created.status_code == 201
    assert created.json()['status'] == 'pending'
    assert eqp_store.loans == []
    # (2) รายละเอียดคำขอมีรายการค้างคืน "ร่ม เกินกำหนด 2 วัน"
    assert detail['outstanding_items'] == [{'item': 'ร่ม', 'days_overdue': 2}]
    # (4) ไม่มีทางอนุมัติแบบปกติ (หลังบ้านบอกว่าถูกบล็อก)
    assert detail['blocked'] is True
    # (3)(4) การแสดงคำเตือนและปุ่มบนหน้าจอ ตรวจด้วย vitest TC-EQP-04-1.test.jsx


def test_TC_EQP_04_2_override_records_loan(eqp_client, eqp_store, student_outstanding, type_id, fixed_now):
    # Given เหมือน TC-EQP-04-1 และเจ้าหน้าที่ตรวจรายการค้างคืนแล้ว
    plug = type_id('ปลั๊กไฟ')
    fixed_now(2026, 11, 12)
    request_id = create_request(eqp_client, student_outstanding.student_id, plug).json()['request_id']
    eqp_client.get(f'/api/loan-requests/{request_id}')

    # When เจ้าหน้าที่กดปลดล็อก (override) โดยไม่ใส่เหตุผล
    response = eqp_client.post(f'/api/loan-requests/{request_id}/override')

    # Then (1) override สำเร็จโดยไม่ต้องใส่เหตุผล
    assert response.status_code == 200
    assert response.json()['override'] is True
    # (2) บันทึกการยืม 1 รายการ due date = วันยืม + 1 วัน
    assert len(eqp_store.loans) == 1
    assert eqp_store.loans[0].due_date == date(2026, 11, 13)
    # (3) ปลั๊กไฟคงเหลือลดจาก 4 เป็น 3
    assert eqp_store.equipment_types[plug].available_count == 3
    # (4) การแสดงผลบนหน้าจอ ตรวจด้วย vitest TC-EQP-04-2.test.jsx


def test_TC_EQP_04_3_returned_but_fine_unpaid(eqp_client, eqp_store, add_student, type_id):
    # Given นักศึกษาคืนของที่ค้างครบแล้ว (รายการค้างคืน 0 รายการ) แต่ยังไม่ชำระค่าปรับ และปลั๊กไฟคงเหลือ 4
    # (ระบบยังไม่มีข้อมูลค่าปรับ Q-08 จึงเตรียมได้แค่รายการค้างคืนว่าง)
    student = add_student('T-0403', outstanding_items=[])
    plug = type_id('ปลั๊กไฟ')

    # When นักศึกษาขอยืมปลั๊กไฟ 1 ชิ้น แล้วเจ้าหน้าที่อนุมัติแบบปกติ
    request_id = create_request(eqp_client, student.student_id, plug).json()['request_id']
    detail = eqp_client.get(f'/api/loan-requests/{request_id}').json()
    response = eqp_client.post(f'/api/loan-requests/{request_id}/approve')

    # Then (1) ระบบไม่บล็อก (Q-08)
    assert detail['blocked'] is False
    # (2) อนุมัติแบบปกติสำเร็จ บันทึกการยืม และปลั๊กไฟคงเหลือเป็น 3
    assert response.status_code == 200
    assert len(eqp_store.loans) == 1
    assert eqp_store.equipment_types[plug].available_count == 3


def test_TC_EQP_04_4_no_outstanding_normal_approve(eqp_client, eqp_store, student_clear, type_id):
    # Given นักศึกษาไม่มีรายการค้างคืน และปลั๊กไฟคงเหลือ 4
    plug = type_id('ปลั๊กไฟ')

    # When นักศึกษาขอยืมปลั๊กไฟ แล้วเจ้าหน้าที่เปิดคำขอ
    request_id = create_request(eqp_client, student_clear.student_id, plug).json()['request_id']
    detail = eqp_client.get(f'/api/loan-requests/{request_id}').json()

    # Then (1) API ส่งรายการค้างคืนว่าง และบอกว่าไม่ถูกบล็อก
    assert detail['outstanding_items'] == []
    assert detail['blocked'] is False
    # (2)(3) การแสดงผลและปุ่มบนหน้าจอ ตรวจด้วย vitest TC-EQP-04-4.test.jsx


def test_TC_EQP_04_5_override_still_checks_stock(eqp_client, eqp_store, student_outstanding, type_id):
    # Given นักศึกษามีรายการค้างคืน มีคำขอยืมร่ม 1 ชิ้นรออนุมัติ แต่ร่มถูกยืมจนคงเหลือ 0 ก่อนเจ้าหน้าที่ตัดสินใจ
    umbrella = type_id('ร่ม')
    request_id = create_request(eqp_client, student_outstanding.student_id, umbrella).json()['request_id']
    eqp_store.equipment_types[umbrella].available_count = 0

    # When เจ้าหน้าที่กดปลดล็อก (override)
    response = eqp_client.post(f'/api/loan-requests/{request_id}/override')

    # Then (1) ได้คำตอบว่า "ไม่สามารถยืมได้"
    assert response.status_code == 409
    assert response.json()['detail'] == 'ไม่สามารถยืมได้'
    # (2) ไม่มีบันทึกการยืม และร่มคงเหลือยังเป็น 0
    assert eqp_store.loans == []
    assert eqp_store.equipment_types[umbrella].available_count == 0
