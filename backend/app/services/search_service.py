from __future__ import annotations

from difflib import SequenceMatcher
from math import ceil
from typing import Any

from app.config import SEARCH_PAGE_SIZE_MAX, SEARCH_PAGE_SIZE_MIN
from app.models.book import BookTitle, build_seed_books


# FR-SRC-01, FR-SRC-02, NFR-PRF-03, IF-CAT-01
# Search service นี้ใช้ข้อมูล seed ของ BookTitle เพื่อคืนผลลัพธ์แบบ title-level พร้อม relevance และ pagination

def _normalize(value: Any) -> str:
    return ' '.join(str(value).lower().split())


def _score_book(book: BookTitle, query: str) -> int:
    normalized_query = _normalize(query)
    if not normalized_query:
        return 0

    search_fields = [book.title, *book.authors, *book.keywords, book.isbn, book.call_number]
    score = 0

    for field in search_fields:
        normalized_field = _normalize(field)
        if not normalized_field:
            continue

        if normalized_field == normalized_query:
            score += 100
        if normalized_field.startswith(normalized_query):
            score += 50
        if normalized_query in normalized_field:
            score += 25

        if SequenceMatcher(None, normalized_query, normalized_field).ratio() >= 0.75:
            score += 45

        for token in normalized_query.split():
            if token and token in normalized_field.split():
                score += 10

    return score


def _serialize_result(book: BookTitle, relevance_score: int) -> dict[str, Any]:
    return {
        'title_id': book.title_id,
        'title': book.title,
        'authors': book.authors,
        'category': book.category,
        'isbn': book.isbn,
        'aggregated_availability': book.aggregated_availability,
        'relevance_score': relevance_score,
    }


def search_books(
    query: str,
    page: int = 1,
    per_page: int = SEARCH_PAGE_SIZE_MIN,
    partial: bool = False,
    database_unavailable: bool = False,
) -> dict[str, Any]:
    """ค้นหาหนังสือแบบ fuzzy/partial match พร้อม partial result และ database unavailable signal"""
    if database_unavailable:
        return {
            'query': query,
            'page': max(1, page),
            'per_page': min(max(per_page, SEARCH_PAGE_SIZE_MIN), SEARCH_PAGE_SIZE_MAX),
            'total': 0,
            'total_pages': 0,
            'results': [],
            'partial': False,
            'database_unavailable': True,
            'message': 'ฐานข้อมูลหนังสือไม่พร้อมใช้งาน',
            'warning': 'ระบบไม่สามารถเรียกข้อมูลหนังสือได้ในขณะนี้',
        }

    normalized_query = _normalize(query)
    books = build_seed_books()

    if normalized_query:
        matches = []
        for book in books:
            score = _score_book(book, normalized_query)
            if score > 0:
                matches.append((score, book))
        matches.sort(key=lambda item: (-item[0], item[1].title.lower()))
        ranked_books = [book for _, book in matches]
    else:
        ranked_books = sorted(books, key=lambda book: book.title.lower())

    total = len(ranked_books)
    page = max(1, page)
    per_page = min(max(per_page, SEARCH_PAGE_SIZE_MIN), SEARCH_PAGE_SIZE_MAX)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_books = ranked_books[start:end]

    results = []
    for book in paginated_books:
        score = _score_book(book, normalized_query) if normalized_query else 0
        results.append(_serialize_result(book, score))

    payload = {
        'query': query,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': max(1, ceil(total / per_page)) if total else 0,
        'results': results,
        'partial': bool(partial),
        'database_unavailable': bool(database_unavailable),
    }

    if partial:
        payload['message'] = 'แสดงผลลัพธ์บางส่วน'
        payload['warning'] = 'ฐานข้อมูลตอบช้า จึงแสดงเท่าที่ดึงมาได้แล้ว'
    elif database_unavailable:
        payload['message'] = 'ฐานข้อมูลหนังสือไม่พร้อมใช้งาน'
        payload['warning'] = 'ระบบไม่สามารถเรียกข้อมูลหนังสือได้ในขณะนี้'
    elif not results:
        payload['message'] = 'ไม่พบข้อมูลหนังสือ'

    return payload
