from app.config import EQUIPMENT_MAX_QUANTITY_PER_REQUEST
from conftest import create_request

# T-17 (FR-EQP-02, Q-11) ตรวจด้วย AC-EQP-03


def test_AC_EQP_03_quantity_over_limit_rejected(eqp_client, eqp_store, student_clear, type_id):
    # Given ถุงผ้าคงเหลือมากกว่าจำนวนสูงสุดต่อคำขอ
    bag = type_id('ถุงผ้า')
    assert eqp_store.equipment_types[bag].available_count > EQUIPMENT_MAX_QUANTITY_PER_REQUEST

    # When นักศึกษาขอยืมเกินจำนวนสูงสุดต่อคำขอ
    response = create_request(eqp_client, student_clear.student_id, bag, quantity=EQUIPMENT_MAX_QUANTITY_PER_REQUEST + 1)

    # Then ระบบแจ้งว่าไม่สามารถยืมได้ และไม่สร้างคำขอ
    assert response.status_code == 409
    assert response.json()['detail'] == 'ไม่สามารถยืมได้'
    assert eqp_store.requests == {}


def test_AC_EQP_03_quantity_at_limit_allowed(eqp_client, eqp_store, student_clear, type_id):
    bag = type_id('ถุงผ้า')
    response = create_request(eqp_client, student_clear.student_id, bag, quantity=EQUIPMENT_MAX_QUANTITY_PER_REQUEST)

    assert response.status_code == 201
    assert response.json()['status'] == 'pending'
