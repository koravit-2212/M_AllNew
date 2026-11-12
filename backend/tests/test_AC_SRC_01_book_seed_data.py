from app.config import BOOK_SEARCH_SEED_DATA, SEARCH_PAGE_SIZE_MIN, SEARCH_PAGE_SIZE_MAX
from app.models.book import BookCopy, BookTitle, build_seed_books


def test_AC_SRC_01_seed_books_support_fuzzy_search_fields():
    books = build_seed_books()

    assert len(books) >= 3
    assert all(isinstance(book, BookTitle) for book in books)

    clean_code = next(book for book in books if book.title == 'Clean Code')
    assert clean_code.authors == ['Robert C. Martin']
    assert 'clean' in clean_code.keywords
    assert clean_code.isbn == '9780132350884'
    assert clean_code.call_number == 'QA76.76.M37'
    assert clean_code.aggregated_availability in {'available', 'mixed', 'borrowed'}


def test_AC_SRC_04_seed_books_include_per_copy_status_and_location():
    books = build_seed_books()
    clean_code = next(book for book in books if book.title == 'Clean Code')

    assert all(isinstance(copy, BookCopy) for copy in clean_code.copies)
    assert len(clean_code.copies) >= 3
    assert any(copy.status == 'available' for copy in clean_code.copies)
    assert any(copy.status == 'borrowed' for copy in clean_code.copies)
    assert all(copy.shelf_location for copy in clean_code.copies)
    assert clean_code.as_detail_payload()['copies'][0]['status'] in {'available', 'borrowed'}

    assert BOOK_SEARCH_SEED_DATA
    assert SEARCH_PAGE_SIZE_MIN == 20
    assert SEARCH_PAGE_SIZE_MAX == 25
