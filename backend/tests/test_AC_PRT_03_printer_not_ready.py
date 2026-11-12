from fastapi.testclient import TestClient

from app.api.printing import get_print_store
from app.main import app
from app.models.printing import build_seed_print_store


# T-07 (FR-PRT-05, IF-PRN-01) ตรวจด้วย AC-PRT-03

def test_AC_PRT_03_PrinterNotReady():
    # Given เครื่องปริ้นไม่พร้อมใช้งาน
    store = build_seed_print_store()
    for printer in store.printers:
        printer.status = 'offline'
    app.dependency_overrides[get_print_store] = lambda: store
    try:
        client = TestClient(app)
        file_id = client.post('/api/print/upload', json={'filename': 'report.pdf', 'size_bytes': 1000}).json()['file_id']

        # When นักศึกษายืนยันการพิมพ์
        response = client.post('/api/print/submit', json={'file_id': file_id, 'pages': 3, 'copies': 1})
        status = client.get('/api/printers/status').json()
    finally:
        app.dependency_overrides.clear()

    # Then ระบบแจ้งเตือนผู้ใช้และไม่ส่งงานพิมพ์
    assert response.status_code == 409
    assert response.json()['detail'] == 'เครื่องพิมพ์ไม่พร้อมใช้งาน'
    assert store.spooler.received_jobs == []
    assert store.jobs == {}
    assert status['printers'] == [{'printer_id': store.printers[0].printer_id, 'status': 'offline', 'ready': False}]


def test_AC_PRT_03_printer_back_ready_can_print():
    store = build_seed_print_store()
    store.printers[0].status = 'error'
    app.dependency_overrides[get_print_store] = lambda: store
    try:
        client = TestClient(app)
        file_id = client.post('/api/print/upload', json={'filename': 'a.pdf', 'size_bytes': 1}).json()['file_id']
        first = client.post('/api/print/submit', json={'file_id': file_id, 'pages': 1, 'copies': 1})
        store.printers[0].status = 'ready'
        second = client.post('/api/print/submit', json={'file_id': file_id, 'pages': 1, 'copies': 1})
    finally:
        app.dependency_overrides.clear()

    assert (first.status_code, second.status_code) == (409, 201)
    assert len(store.spooler.received_jobs) == 1
