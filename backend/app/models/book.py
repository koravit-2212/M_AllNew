from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.config import BOOK_SEARCH_SEED_DATA


@dataclass
class BookCopy:
    """รองรับ FR-SRC-02, FR-SRC-03 และ IF-CAT-01 สำหรับสถานะ per-copy และตำแหน่งจัดเก็บ"""

    copy_id: str
    title_id: str
    status: str
    shelf_location: str
    location_detail: str

    def as_dict(self) -> dict[str, Any]:
        return {
            'copy_id': self.copy_id,
            'title_id': self.title_id,
            'status': self.status,
            'shelf_location': self.shelf_location,
            'location_detail': self.location_detail,
        }


@dataclass
class BookTitle:
    """รองรับ FR-SRC-01, FR-SRC-02, FR-SRC-03 และ IF-CAT-01 สำหรับข้อมูลหนังสือและผลรวมสถานะ"""

    title_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    category: str = ''
    isbn: str = ''
    call_number: str = ''
    copies: list[BookCopy] = field(default_factory=list)

    @property
    def aggregated_availability(self) -> str:
        statuses = [copy.status for copy in self.copies]
        if not statuses:
            return 'unavailable'
        if all(status == 'available' for status in statuses):
            return 'available'
        if all(status == 'borrowed' for status in statuses):
            return 'borrowed'
        return 'mixed'

    def as_detail_payload(self) -> dict[str, Any]:
        return {
            'title_id': self.title_id,
            'title': self.title,
            'authors': self.authors,
            'isbn': self.isbn,
            'call_number': self.call_number,
            'category': self.category,
            'copies': [copy.as_dict() for copy in self.copies],
            'aggregated_availability': self.aggregated_availability,
        }


def build_seed_books() -> list[BookTitle]:
    """สร้างข้อมูลตัวอย่างที่ครอบคลุมการค้นหา fuzzy/partial และ per-copy status ตาม AC-SRC-01, AC-SRC-04"""

    books: list[BookTitle] = []
    for payload in BOOK_SEARCH_SEED_DATA:
        copies = [
            BookCopy(
                copy_id=item['copy_id'],
                title_id=item['title_id'],
                status=item['status'],
                shelf_location=item['shelf_location'],
                location_detail=item['location_detail'],
            )
            for item in payload['copies']
        ]
        books.append(
            BookTitle(
                title_id=payload['title_id'],
                title=payload['title'],
                authors=payload['authors'],
                keywords=payload['keywords'],
                category=payload['category'],
                isbn=payload['isbn'],
                call_number=payload['call_number'],
                copies=copies,
            )
        )
    return books
