from fastapi.testclient import TestClient

from app.api.printing import get_print_store
from app.config import PRINT_RATE_PER_PAGE_BAHT
from app.main import app
from app.models.printing import build_seed_print_store


# T-03 (FR-PRT-01, FR-PRT-02) ตรวจด้วย AC-PRT-01

def _client():
    store = build_seed_print_store()
    app.dependency_overrides[get_print_store] = lambda: store
    return store, TestClient(app)


def test_AC_PRT_01_CostPreview():
    store, client = _client()
    try:
        # Given นักศึกษาเลือกไฟล์ที่รองรับ
        uploaded = client.post('/api/print/upload', json={'filename': 'report.pdf', 'content_type': 'application/pdf', 'size_bytes': 1_200_000})
        file_id = uploaded.json()['file_id']

        # When นักศึกษากำหนดจำนวนหน้าและจำนวนชุด
        bw = client.get('/api/print/options', params={'file_id': file_id, 'pages': 12, 'copies': 2, 'color_mode': 'BW'}).json()
        color = client.get('/api/print/options', params={'file_id': file_id, 'pages': 12, 'copies': 2, 'color_mode': 'Color'}).json()
    finally:
        app.dependency_overrides.clear()

    # Then ระบบแสดงตัวเลือกการพิมพ์และค่าใช้บริการที่คำนวณถูกต้องก่อนให้ยืนยัน
    assert uploaded.status_code == 201
    assert file_id in store.files
    assert {m['code'] for m in bw['allowed_color_modes']} == set(PRINT_RATE_PER_PAGE_BAHT)
    assert bw['total_pages'] == 24
    assert bw['estimated_cost'] == 24 * PRINT_RATE_PER_PAGE_BAHT['BW']
    assert color['estimated_cost'] == 24 * PRINT_RATE_PER_PAGE_BAHT['Color']
    assert store.jobs == {}


def test_AC_PRT_01_invalid_inputs():
    store, client = _client()
    try:
        file_id = client.post('/api/print/upload', json={'filename': 'a.pdf', 'size_bytes': 10}).json()['file_id']
        zero_pages = client.get('/api/print/options', params={'file_id': file_id, 'pages': 0, 'copies': 1})
        bad_mode = client.get('/api/print/options', params={'file_id': file_id, 'pages': 1, 'copies': 1, 'color_mode': 'X'})
        missing = client.get('/api/print/options', params={'file_id': 'nope', 'pages': 1, 'copies': 1})
    finally:
        app.dependency_overrides.clear()

    assert zero_pages.status_code == 422
    assert bad_mode.status_code == 422
    assert missing.status_code == 404
