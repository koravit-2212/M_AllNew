from fastapi.testclient import TestClient

from app.main import app


def test_AC_SRC_03_database_unavailable_returns_clear_error_message():
    """Given the library database is unavailable, When the search endpoint is called, Then it returns a clear database-down message instead of a misleading no-results message."""
    client = TestClient(app)

    response = client.get(
        '/api/search',
        params={'q': 'clean', 'page': 1, 'per_page': 20, 'database_unavailable': True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['results'] == []
    assert payload['total'] == 0
    assert payload['partial'] is False
    assert payload['database_unavailable'] is True
    assert payload['message'] == 'ฐานข้อมูลหนังสือไม่พร้อมใช้งาน'
