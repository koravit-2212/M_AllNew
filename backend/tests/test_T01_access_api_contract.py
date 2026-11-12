from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_T01_access_routes_expose_contract():
    # Given ในเฟส 0 ระบบต้องมี contract API สำหรับ scan flow ที่พร้อมให้เฟสต่อไปใช้
    response = client.get('/api/access/status')
    assert response.status_code == 200
    payload = response.json()
    assert {'currentOccupancy', 'lastUpdatedAt'} <= set(payload)

    # When เริ่มสแกน QR Code หรือบัตรนักศึกษา
    scan = client.post('/api/access/scan', json={'scanMethod': 'qr', 'qrCodeOrCardId': 'STD-12345'})
    assert scan.status_code == 200
    scan_payload = scan.json()
    assert {'status', 'allowed', 'message', 'eventId'} <= set(scan_payload)

    # Then ระบบต้องคืน contract สำหรับ manual verification ที่รวม audit log ให้พร้อมต่อ FF
    event_id = scan_payload['eventId']
    verify = client.post(
        '/api/access/verify-manual',
        json={'eventId': event_id, 'staffId': 'ST-1001', 'reason': 'ยืนยันด้วยมือ', 'manualApproved': True},
    )
    assert verify.status_code == 200
    verify_payload = verify.json()
    assert {'auditId', 'approved', 'message'} <= set(verify_payload)
