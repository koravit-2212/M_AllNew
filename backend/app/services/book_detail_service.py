from __future__ import annotations

from typing import Any

from app.models.book import build_seed_books


# FR-SRC-02, FR-SRC-03, IF-CAT-01
# Service นี้อ่านข้อมูลหนังสือจากชุดข้อมูลตัวอย่าง Central Library DB และคืนค่า per-copy status พร้อมตำแหน่งจัดเก็บ

def get_book_detail(title_id: str) -> dict[str, Any] | None:
    for book in build_seed_books():
        if book.title_id == title_id:
            return {
                'title_id': book.title_id,
                'title': book.title,
                'authors': book.authors,
                'isbn': book.isbn,
                'call_number': book.call_number,
                'category': book.category,
                'copies': [copy.as_dict() for copy in book.copies],
                'aggregated_availability': book.aggregated_availability,
            }
    return None
