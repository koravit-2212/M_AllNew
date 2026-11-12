from fastapi.testclient import TestClient

from app.main import app


def test_AC_SRC_04_book_detail_fields():
    """Given a selected title from the search results, When the book detail endpoint is called, Then it returns the required title and per-copy status fields."""
    client = TestClient(app)

    response = client.get('/api/books/bk-clean-code')

    assert response.status_code == 200
    payload = response.json()

    assert payload['title'] == 'Clean Code'
    assert payload['authors'] == ['Robert C. Martin']
    assert payload['isbn'] == '9780132350884'
    assert payload['call_number'] == 'QA76.76.M37'
    assert payload['category'] == 'วิศวกรรมซอฟต์แวร์'
    assert payload['aggregated_availability'] in {'available', 'mixed', 'borrowed'}
    assert isinstance(payload['copies'], list)
    assert payload['copies']

    first_copy = payload['copies'][0]
    assert 'copy_id' in first_copy
    assert 'status' in first_copy
    assert 'shelf_location' in first_copy
    assert first_copy['status'] in {'available', 'borrowed', 'reserved'}
