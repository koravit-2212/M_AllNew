from fastapi.testclient import TestClient

from app.main import app


def test_AC_SRC_02_search_api_returns_no_results_message():
    """Given a search term that matches no books, When the API is called, Then it returns an empty result set with a clear no-result message."""
    client = TestClient(app)

    response = client.get('/api/search', params={'q': 'xyzqwe', 'page': 1, 'per_page': 20})

    assert response.status_code == 200
    payload = response.json()
    assert payload['results'] == []
    assert payload['total'] == 0
    assert payload['message'] == 'ไม่พบข้อมูลหนังสือ'
