from fastapi.testclient import TestClient

from app.main import app


def test_AC_SRC_01_search_api_returns_relevant_title_results_with_pagination():
    """Given a partial book title search, When the search endpoint is called, Then it returns title-level relevance results within a paginated response."""
    client = TestClient(app)

    response = client.get('/api/search', params={'q': 'clen cod', 'page': 1, 'per_page': 20})

    assert response.status_code == 200
    payload = response.json()

    assert payload['page'] == 1
    assert payload['per_page'] == 20
    assert payload['total'] >= 1
    assert payload['results']
    assert len(payload['results']) <= payload['per_page']

    first_result = payload['results'][0]
    assert first_result['title'] == 'Clean Code'
    assert 'title_id' in first_result
    assert 'authors' in first_result
    assert 'aggregated_availability' in first_result
    assert first_result['aggregated_availability'] in {'available', 'mixed', 'borrowed'}
    assert 'relevance_score' in first_result
    assert first_result['relevance_score'] >= 0
