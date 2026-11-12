from fastapi.testclient import TestClient

from app.api.printing import get_print_store
from app.config import PRINT_RATE_PER_PAGE_BAHT
from app.main import app
from app.models.printing import build_seed_print_store


# T-05 (FR-PRT-03, IF-PRN-01) ตรวจด้วย AC-PRT-02

def test_AC_PRT_02_PrintFlow():
    # Given เครื่องปริ้นพร้อมใช้งานและไฟล์รองรับ
    store = build_seed_print_store()
    assert all(p.is_ready for p in store.printers)
    app.dependency_overrides[get_print_store] = lambda: store
    try:
        client = TestClient(app)
        file_id = client.post('/api/print/upload', json={'filename': 'report.pdf', 'content_type': 'application/pdf', 'size_bytes': 1000}).json()['file_id']

        # When นักศึกษายืนยันการพิมพ์
        submitted = client.post('/api/print/submit', json={'file_id': file_id, 'pages': 12, 'copies': 2, 'color_mode': 'BW'})
        job = client.get(f"/api/print/jobs/{submitted.json()['printjob_id']}")
    finally:
        app.dependency_overrides.clear()

    # Then ระบบส่งงานไปยังเครื่องปริ้นและนักศึกษาได้รับเอกสารตามจำนวนที่กำหนด
    assert submitted.status_code == 201
    assert submitted.json()['status'] == 'sent'
    assert len(store.spooler.received_jobs) == 1
    sent = store.spooler.received_jobs[0]
    assert (sent['pages'], sent['copies'], sent['color_mode']) == (12, 2, 'BW')
    assert sent['printer_id'] == store.printers[0].printer_id
    # บันทึกข้อมูลการใช้บริการ
    assert job.status_code == 200
    assert job.json()['total_pages'] == 24
    assert job.json()['total_cost'] == 24 * PRINT_RATE_PER_PAGE_BAHT['BW']
    assert job.json()['filename'] == 'report.pdf'


def test_AC_PRT_02_unknown_file_or_job():
    store = build_seed_print_store()
    app.dependency_overrides[get_print_store] = lambda: store
    try:
        client = TestClient(app)
        r1 = client.post('/api/print/submit', json={'file_id': 'nope', 'pages': 1, 'copies': 1})
        r2 = client.get('/api/print/jobs/JOB-9999')
    finally:
        app.dependency_overrides.clear()

    assert (r1.status_code, r2.status_code) == (404, 404)
    assert store.spooler.received_jobs == []
