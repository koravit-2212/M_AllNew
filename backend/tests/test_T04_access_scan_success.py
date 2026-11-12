from fastapi.testclient import TestClient

from app.api.access import get_access_store
from app.main import app
from app.models.facility_occupancy import build_seed_access_store


def test_AC_ACC_01_successful_access_scan():
    # Given นักศึกษามีบัตรนักศึกษาที่ถูกต้องและมีสิทธิ์เข้าใช้บริการ
    store = build_seed_access_store()
    app.dependency_overrides[get_access_store] = lambda: store
    try:
        # When นักศึกษาสแกน QR Code ที่เครื่องอ่าน
        response = TestClient(app).post('/api/access/scan', json={'scanMethod': 'qr', 'qrCodeOrCardId': 'STD-1001'})
    finally:
        app.dependency_overrides.clear()

    # Then ระบบยืนยันตัวตนสำเร็จ อนุญาตให้เข้าใช้ห้องสมุด และบันทึกข้อมูลการเข้าใช้บริการ
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'approved'
    assert payload['allowed'] is True
    assert payload['message'] == 'ยืนยันตัวตนสำเร็จ'
    assert payload['memberId'] == 'STD-1001'
    assert payload['memberName'] == 'นักศึกษาตัวอย่าง ก'
    assert payload['currentOccupancy'] == 129
    assert len(store.events) == 1
    assert store.events[0].result_status == 'approved'
