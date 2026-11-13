from __future__ import annotations

from dataclasses import dataclass, field

from app.models.book_copy import BookCopy
from app.models.loan_record import LoanRecord
from app.models.notification_log import NotificationLog
from app.models.return_audit_log import ReturnAuditLog


@dataclass
class LoanRepository:
    """รองรับ FR-LNS-02, FR-LNS-04, FR-LNS-05, FR-LNS-06, CON-LNS-01, CON-LNS-02: เก็บข้อมูลเล่มหนังสือ รายการยืม การแจ้งเตือน และ audit log คืนหนังสือ"""

    book_copies: dict[str, BookCopy] = field(default_factory=dict)
    loan_records: list[LoanRecord] = field(default_factory=list)
    notifications: list[NotificationLog] = field(default_factory=list)
    return_audit_logs: list[ReturnAuditLog] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.book_copies:
            self.book_copies = {
                'CC-001': BookCopy(
                    copy_id='CC-001',
                    title_id='bk-clean-code',
                    title='Clean Code',
                    barcode='BC-001',
                    status='available',
                    availability='available',
                ),
                'CC-002': BookCopy(
                    copy_id='CC-002',
                    title_id='bk-clean-code',
                    title='Clean Code',
                    barcode='BC-002',
                    status='available',
                    availability='available',
                ),
            }

    def copy_for(self, copy_id: str) -> BookCopy | None:
        return self.book_copies.get(copy_id)

    def copy_for_barcode(self, barcode: str) -> BookCopy | None:
        return next((copy for copy in self.book_copies.values() if copy.barcode == barcode), None)

    def member_active_loan_count(self, member_id: str) -> int:
        return sum(
            1 for record in self.loan_records if record.member_id == member_id and record.status == 'borrowed'
        )

    def copy_is_borrowed(self, copy_id: str) -> bool:
        copy = self.copy_for(copy_id)
        if copy is not None:
            if copy.status == 'borrowed' or copy.availability == 'borrowed':
                return True

        return any(
            record.copy_id == copy_id and record.status == 'borrowed'
            for record in self.loan_records
        )

    def find_active_loan(self, member_id: str, copy_id: str) -> LoanRecord | None:
        for record in reversed(self.loan_records):
            if record.member_id == member_id and record.copy_id == copy_id and record.status == 'borrowed':
                return record
        return None

    def add_loan_record(self, record: LoanRecord) -> LoanRecord:
        self.loan_records.append(record)
        copy = self.copy_for(record.copy_id)
        if copy is not None:
            copy.status = 'borrowed'
            copy.availability = 'borrowed'
            copy.last_loan_record_id = record.loan_id
        return record

    def add_notification_log(self, log: NotificationLog) -> NotificationLog:
        self.notifications.append(log)
        return log

    def add_return_audit_log(self, log: ReturnAuditLog) -> ReturnAuditLog:
        self.return_audit_logs.append(log)
        return log

    def loan_history_for_member(self, member_id: str) -> list[dict]:
        """FR-LNS-07: คืนประวัติการยืม-คืนที่ถูกต้องจากข้อมูลจริงใน repository ของสมาชิกที่ร้องขอ"""
        records: list[dict] = []
        for record in self.loan_records:
            if record.member_id != member_id:
                continue

            borrow_date = (record.borrow_time or '').split('T', 1)[0]
            return_date = (record.return_time or '').split('T', 1)[0] if record.return_time else None
            records.append(
                {
                    'loan_id': record.loan_id,
                    'copy_id': record.copy_id,
                    'borrow_date': borrow_date,
                    'due_date': record.due_date,
                    'return_date': return_date,
                    'status': record.status,
                    'overdue_days': record.overdue_days,
                    'penalty_amount': record.penalty_amount,
                }
            )

        records.sort(key=lambda item: (item['borrow_date'] or '', item['loan_id']))
        return records
