from fastapi.testclient import TestClient

from app.api.printing import get_print_store
from app.config import PRINT_ALLOWED_EXTENSIONS, PRINT_MAX_FILE_SIZE_BYTES
from app.main import app
from app.models.printing import build_seed_print_store


# T-09 (FR-PRT-04, CON-FILE-01) ตรวจด้วย AC-PRT-04

def _client():
    store = build_seed_print_store()
    app.dependency_overrides[get_print_store] = lambda: store
    return store, TestClient(app)


def test_AC_PRT_04_UnsupportedFile():
    store, client = _client()
    try:
        # Given ไฟล์ที่เลือกไม่รองรับ (ชนิดไม่รองรับ / ขนาดเกิน 50 MB)
        # When นักศึกษาเลือกไฟล์
        exe = client.post('/api/print/upload', json={'filename': 'setup.exe', 'size_bytes': 1000})
        too_big = client.post('/api/print/upload', json={'filename': 'big.pdf', 'size_bytes': PRINT_MAX_FILE_SIZE_BYTES + 1})
        submit = client.post('/api/print/submit', json={'file_id': 'FILE-0001', 'pages': 1, 'copies': 1})
    finally:
        app.dependency_overrides.clear()

    # Then ระบบแจ้งเตือนและไม่ให้ดำเนินการพิมพ์ต่อ
    for response in (exe, too_big):
        assert response.status_code == 415
        assert response.json()['detail']['message'] == 'ไม่รองรับไฟล์ชนิดนี้'
        assert response.json()['detail']['allowed_extensions'] == list(PRINT_ALLOWED_EXTENSIONS)
        assert 'file_id' not in response.json()
    assert store.files == {}
    assert submit.status_code == 404
    assert store.spooler.received_jobs == []


def test_AC_PRT_04_all_allowed_types_and_exact_limit_accepted():
    store, client = _client()
    try:
        results = [
            client.post('/api/print/upload', json={'filename': f'file.{ext.upper()}', 'size_bytes': PRINT_MAX_FILE_SIZE_BYTES})
            for ext in PRINT_ALLOWED_EXTENSIONS
        ]
        no_ext = client.post('/api/print/upload', json={'filename': 'README', 'size_bytes': 1})
    finally:
        app.dependency_overrides.clear()

    assert all(r.status_code == 201 for r in results)
    assert no_ext.status_code == 415
    assert len(store.files) == len(PRINT_ALLOWED_EXTENSIONS)
