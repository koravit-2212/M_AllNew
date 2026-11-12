from datetime import date

from conftest import create_request

# test จาก specs/007-equipment/test-cases.md (AC-EQP-02) ห้ามแก้ให้ผ่าน


def test_TC_EQP_02_1_approve_records_loan_and_reduces_stock(eqp_client, eqp_store, student_clear, type_id, fixed_now):
    # Given ปลั๊กไฟคงเหลือ 4 นักศึกษาไม่มีรายการค้างคืน มีคำขอยืมปลั๊กไฟ 1 ชิ้นรออนุมัติ วันที่ยืม 2569-11-12
    plug = type_id('ปลั๊กไฟ')
    assert eqp_store.equipment_types[plug].available_count == 4
    fixed_now(2026, 11, 12)
    request_id = create_request(eqp_client, student_clear.student_id, plug).json()['request_id']

    # When เจ้าหน้าที่อนุมัติการยืม
    response = eqp_client.post(f'/api/loan-requests/{request_id}/approve')

    # Then (1) บันทึกการยืม 1 รายการ นักศึกษา ประเภท และจำนวนตรงกับคำขอ
    assert response.status_code == 200
    assert len(eqp_store.loans) == 1
    loan = eqp_store.loans[0]
    assert (loan.student_id, loan.equipment_type_id, loan.quantity) == (student_clear.student_id, plug, 1)
    # (2) due date คือ 2569-11-13
    assert loan.due_date == date(2026, 11, 13)
    assert response.json()['due_date'] == '2026-11-13'
    # (3) ปลั๊กไฟคงเหลือลดจาก 4 เป็น 3
    assert eqp_store.equipment_types[plug].available_count == 3
    assert response.json()['available_count'] == 3
    # (4) คำขอเปลี่ยนเป็นอนุมัติแล้ว
    assert eqp_store.requests[request_id].status == 'approved'
    # (5) การแสดงผลบนหน้าจอเจ้าหน้าที่ ตรวจด้วย vitest TC-EQP-02-1.test.jsx


def test_TC_EQP_02_2_staff_reviews_before_approve(eqp_client, eqp_store, student_clear, type_id):
    # Given ปลั๊กไฟคงเหลือ 4 นักศึกษาไม่มีรายการค้างคืน
    plug = type_id('ปลั๊กไฟ')

    # When นักศึกษาส่งคำขอยืมปลั๊กไฟ 1 ชิ้น แล้วเจ้าหน้าที่เปิดคำขอนั้น ยังไม่กดอนุมัติ
    created = create_request(eqp_client, student_clear.student_id, plug)
    request_id = created.json()['request_id']
    detail = eqp_client.get(f'/api/loan-requests/{request_id}').json()

    # Then (1) คำขอสถานะรออนุมัติ และยังไม่มีบันทึกการยืม
    assert created.json()['status'] == 'pending'
    assert eqp_store.loans == []
    # (2) ปลั๊กไฟคงเหลือยังเป็น 4
    assert eqp_store.equipment_types[plug].available_count == 4
    # (3) เจ้าหน้าที่เห็นชื่อและรหัสนักศึกษา อุปกรณ์และจำนวน และไม่มีรายการค้างคืน
    assert detail['student'] == {'student_id': student_clear.student_id, 'name': student_clear.name}
    assert detail['equipment']['name'] == 'ปลั๊กไฟ'
    assert detail['quantity'] == 1
    assert detail['outstanding_items'] == []


def test_TC_EQP_02_3_last_item_then_insufficient(eqp_client, eqp_store, add_student, type_id):
    # Given ร่มคงเหลือ 1 มีคำขอยืมร่ม 1 ชิ้นรออนุมัติ 2 คำขอ จากนักศึกษาไม่มีรายการค้างคืน 2 คน
    umbrella = type_id('ร่ม')
    eqp_store.equipment_types[umbrella].available_count = 1
    first_student = add_student('T-0201')
    second_student = add_student('T-0202')
    first = create_request(eqp_client, first_student.student_id, umbrella).json()['request_id']
    second = create_request(eqp_client, second_student.student_id, umbrella).json()['request_id']

    # When เจ้าหน้าที่อนุมัติคำขอแรก แล้วอนุมัติคำขอที่สอง
    r1 = eqp_client.post(f'/api/loan-requests/{first}/approve')
    r2 = eqp_client.post(f'/api/loan-requests/{second}/approve')

    # Then (1) คำขอแรกถูกบันทึก และร่มคงเหลือเป็น 0
    assert r1.status_code == 200
    assert [loan.request_id for loan in eqp_store.loans] == [first]
    # (2) คำขอที่สองได้คำตอบว่า "ไม่สามารถยืมได้"
    assert r2.status_code == 409
    assert r2.json()['detail'] == 'ไม่สามารถยืมได้'
    # (3) ไม่มีบันทึกการยืมของคำขอที่สอง และคงเหลือยังเป็น 0 ไม่ติดลบ
    assert all(loan.request_id != second for loan in eqp_store.loans)
    assert eqp_store.equipment_types[umbrella].available_count == 0


def test_TC_EQP_02_4_due_date_one_day_month_end_bangkok(eqp_client, eqp_store, student_clear, type_id, fixed_now):
    # Given ถุงผ้าคงเหลือ 5 นักศึกษาไม่มีรายการค้างคืน อนุมัติ 2569-11-30 เวลา 23:30 น. ตามเวลาไทย
    bag = type_id('ถุงผ้า')
    fixed_now(2026, 11, 30, 23, 30)
    request_id = create_request(eqp_client, student_clear.student_id, bag).json()['request_id']

    # When เจ้าหน้าที่อนุมัติการยืมถุงผ้า 1 ชิ้น
    response = eqp_client.post(f'/api/loan-requests/{request_id}/approve')

    # Then (1) วันที่ยืมคือ 2569-11-30 ตามเวลาไทย ไม่ใช่ UTC
    assert response.status_code == 200
    assert eqp_store.loans[0].loan_date == date(2026, 11, 30)
    # (2) due date คือ 2569-12-01
    assert eqp_store.loans[0].due_date == date(2026, 12, 1)


def test_TC_EQP_02_5_outstanding_blocks_normal_approve(eqp_client, eqp_store, student_outstanding, type_id):
    # Given ปลั๊กไฟคงเหลือ 4 แต่นักศึกษามีรายการค้างคืน และมีคำขอยืม 1 ชิ้นรออนุมัติ
    plug = type_id('ปลั๊กไฟ')
    request_id = create_request(eqp_client, student_outstanding.student_id, plug).json()['request_id']

    # When เจ้าหน้าที่อนุมัติการยืมแบบปกติ
    response = eqp_client.post(f'/api/loan-requests/{request_id}/approve')

    # Then (1) ระบบปฏิเสธการอนุมัติปกติ
    assert response.status_code == 409
    # (2) ไม่มีบันทึกการยืม
    assert eqp_store.loans == []
    # (3) ปลั๊กไฟคงเหลือยังเป็น 4
    assert eqp_store.equipment_types[plug].available_count == 4
    # (4) คำขอยังรออนุมัติ
    assert eqp_store.requests[request_id].status == 'pending'
