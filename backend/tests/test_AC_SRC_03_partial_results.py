from fastapi.testclient import TestClient

from app.main import app


def test_AC_SRC_03_search_api_exposes_partial_results_signal():
    """Given the book database is slow or incomplete, When the search endpoint is called with a partial signal, Then it returns the available results and marks them as partial."""
    client = TestClient(app)

    response = client.get('/api/search', params={'q': 'clean', 'page': 1, 'per_page': 20, 'partial': True})

    assert response.status_code == 200
    payload = response.json()
    assert payload['partial'] is True
    assert payload['message'] == 'แสดงผลลัพธ์บางส่วน'
    assert payload['warning'] == 'ฐานข้อมูลตอบช้า จึงแสดงเท่าที่ดึงมาได้แล้ว'
    assert payload['results']
    assert len(payload['results']) <= payload['per_page']
