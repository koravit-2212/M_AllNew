from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BookCopy:
    """รองรับ FR-LNS-01, FR-LNS-02, FR-LNS-04, FR-LNS-05 และ CON-LNS-01, CON-LNS-02 สำหรับข้อมูลเล่มหนังสือที่พร้อมยืม-คืน"""

    copy_id: str
    title_id: str
    title: str
    barcode: str
    status: str = 'available'
    availability: str = 'available'
    last_loan_record_id: str | None = None

    @property
    def is_available(self) -> bool:
        return self.status == 'available' and self.availability == 'available'

    def as_dict(self) -> dict[str, Any]:
        return {
            'copy_id': self.copy_id,
            'title_id': self.title_id,
            'title': self.title,
            'barcode': self.barcode,
            'status': self.status,
            'availability': self.availability,
            'last_loan_record_id': self.last_loan_record_id,
        }
