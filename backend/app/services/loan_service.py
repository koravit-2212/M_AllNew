from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from app.config import (
    BOOK_GENERAL_PENALTY_PER_DAY_BAHT,
    BOOK_SPECIAL_PENALTY_PER_DAY_BAHT,
    DEFAULT_MAX_BOOKS_PER_MEMBER,
    LOAN_DUE_DAYS,
)
from app.models.loan_record import LoanRecord
from app.models.return_audit_log import ReturnAuditLog
from app.repositories.loan_repository import LoanRepository
from app.services.notification_service import schedule_due_reminders


class LoanService:
    """รองรับ FR-LNS-02, FR-LNS-04, CON-LNS-01: ตรวจสิทธิ์การยืมและส่งเหตุผลที่ชัดเจนให้หน้าจอหรือ API ใช้ต่อได้"""

    def __init__(self, repository: LoanRepository | None = None):
        self.repository = repository or LoanRepository()

    def validate_loan(
        self,
        member_id: str,
        copy_id: str,
        max_books_per_member: int | None = None,
    ) -> dict:
        normalized_member_id = (member_id or '').strip()
        normalized_copy_id = (copy_id or '').strip()

        if not normalized_member_id:
            return {
                'allowed': False,
                'status': 'invalid_member',
                'message': 'ไม่พบข้อมูลสมาชิก',
            }

        if not normalized_copy_id:
            return {
                'allowed': False,
                'status': 'invalid_copy',
                'message': 'ไม่พบข้อมูลหนังสือ',
            }

        if self.repository.copy_is_borrowed(normalized_copy_id):
            return {
                'allowed': False,
                'status': 'copy_unavailable',
                'message': 'หนังสือเล่มนี้ถูกยืมอยู่แล้ว',
            }

        limit = DEFAULT_MAX_BOOKS_PER_MEMBER if max_books_per_member is None else max_books_per_member
        if self.repository.member_active_loan_count(normalized_member_id) >= limit:
            return {
                'allowed': False,
                'status': 'borrow_limit_exceeded',
                'message': 'ยืมครบจำนวนหนังสือที่สามารถยืมได้แล้ว',
            }

        return {
            'allowed': True,
            'status': 'eligible',
            'message': 'สามารถยืมหนังสือได้',
        }

    @staticmethod
    def penalty_rate_for_copy(copy_title: str | None) -> int:
        """FR-LNS-06, ASM-03: ใช้อัตราค่าปรับตามประเภทหนังสือ โดยหนังสือทั่วไป 3 บาท/วัน และหนังสือสำรอง/สื่อ/อุปกรณ์ 20 บาท/วัน"""
        candidate = (copy_title or '').lower()
        special_keywords = ('media', 'audiovisual', 'equipment', 'reserve', 'special', 'โสต', 'สื่อ', 'อุปกรณ์', 'สำรอง')
        if any(keyword in candidate for keyword in special_keywords):
            return BOOK_SPECIAL_PENALTY_PER_DAY_BAHT
        return BOOK_GENERAL_PENALTY_PER_DAY_BAHT

    def borrow_book(self, member_id: str, copy_id: str, source: str = 'counter') -> dict:
        """FR-LNS-01, FR-LNS-02, FR-LNS-03: ยืมหนังสือ ถ้าผ่านความถูกต้องจะบันทึก loan และสร้าง notification schedule"""

        normalized_member_id = (member_id or '').strip()
        normalized_copy_id = (copy_id or '').strip()
        validation = self.validate_loan(normalized_member_id, normalized_copy_id, DEFAULT_MAX_BOOKS_PER_MEMBER)
        if not validation['allowed']:
            return {
                'allowed': False,
                'status': validation['status'],
                'message': validation['message'],
            }

        due_date = (date.today() + timedelta(days=LOAN_DUE_DAYS)).isoformat()
        loan_id = f'loan-{uuid4().hex[:10]}'
        loan_record = LoanRecord(
            loan_id=loan_id,
            member_id=normalized_member_id,
            copy_id=normalized_copy_id,
            borrow_time=date.today().isoformat(),
            due_date=due_date,
            return_time=None,
            status='borrowed',
            overdue_days=0,
            penalty_amount=0,
        )
        self.repository.add_loan_record(loan_record)

        notifications = schedule_due_reminders(normalized_member_id, loan_id, due_date)
        for notification in notifications:
            self.repository.add_notification_log(notification)

        return {
            'allowed': True,
            'status': 'approved',
            'loan_id': loan_id,
            'due_date': due_date,
            'message': 'ยืมสำเร็จ',
            'source': source,
            'notifications': [item.as_dict() for item in notifications],
        }

    def return_book(self, member_id: str, copy_id: str, actor: str = 'system') -> dict:
        """FR-LNS-05, FR-LNS-06: คืนหนังสือ, คำนวณ overdue_days และ penalty_amount, และบันทึก audit log ให้เจ้าหน้าที่ตรวจสอบ"""
        normalized_member_id = (member_id or '').strip()
        normalized_copy_id = (copy_id or '').strip()

        if not normalized_member_id:
            return {'allowed': False, 'status': 'invalid_member', 'message': 'ไม่พบข้อมูลสมาชิก'}
        if not normalized_copy_id:
            return {'allowed': False, 'status': 'invalid_copy', 'message': 'ไม่พบข้อมูลหนังสือ'}

        copy = self.repository.copy_for(normalized_copy_id)
        if copy is None:
            return {'allowed': False, 'status': 'copy_not_found', 'message': 'ไม่พบข้อมูลหนังสือ'}

        loan_record = self.repository.find_active_loan(normalized_member_id, normalized_copy_id)
        if loan_record is None:
            return {'allowed': False, 'status': 'loan_not_found', 'message': 'ไม่พบรายการยืมที่ต้องคืน'}

        due_date = loan_record.due_date or date.today().isoformat()
        today = date.today()
        overdue_days = max(0, (today - date.fromisoformat(due_date)).days)
        penalty_rate = self.penalty_rate_for_copy(copy.title)
        penalty_amount = overdue_days * penalty_rate if overdue_days > 0 else 0

        loan_record.status = 'returned'
        loan_record.return_time = today.isoformat()
        loan_record.overdue_days = overdue_days
        loan_record.penalty_amount = penalty_amount

        copy.status = 'available'
        copy.availability = 'available'

        audit = ReturnAuditLog(
            audit_id=f'audit-{uuid4().hex[:10]}',
            loan_id=loan_record.loan_id,
            member_id=normalized_member_id,
            overdue_days=overdue_days,
            penalty_amount=penalty_amount,
            processed_at=today.isoformat(),
            actor=actor,
        )
        self.repository.add_return_audit_log(audit)

        message = 'คืนสำเร็จ' if overdue_days == 0 else f'คืนสำเร็จ เกินกำหนด {overdue_days} วัน ค่าปรับ {penalty_amount} บาท'
        return {
            'allowed': True,
            'status': 'returned',
            'loan_id': loan_record.loan_id,
            'return_status': 'returned',
            'overdue_days': overdue_days,
            'penalty_amount': penalty_amount,
            'message': message,
            'audit_log': audit.as_dict(),
        }

    def member_history(self, member_id: str) -> list[dict]:
        """FR-LNS-07: คืนประวัติยืมคืนจริงจาก repository ของสมาชิกที่ร้องขอ"""
        normalized_member_id = (member_id or '').strip()
        if not normalized_member_id:
            return []
        return self.repository.loan_history_for_member(normalized_member_id)
