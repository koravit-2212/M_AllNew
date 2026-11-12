from fastapi.testclient import TestClient

from app.main import app


def test_AC_SRC_03_search_health_reports_index_status_and_sync_details():
    """Given search index is active, When client requests the health endpoint, Then it gets index status and sync metadata."""
    client = TestClient(app)

    response = client.get('/api/health/search')

    assert response.status_code == 200
    payload = response.json()
    assert 'index_status' in payload
    assert 'last_sync_time' in payload
    assert 'sync_health' in payload
    assert payload['index_status'] in {'healthy', 'degraded', 'offline'}
    assert payload['sync_health'] in {'ok', 'warning', 'error'}
    assert payload['last_sync_time']
