from app.models.book_copy import BookCopy
from app.models.loan_record import LoanRecord
from app.models.notification_log import NotificationLog
from app.models.return_audit_log import ReturnAuditLog


# T-01 (FR-LNS-01, FR-LNS-02, FR-LNS-05, CON-LNS-01, CON-LNS-02) งานพื้นฐาน ไม่มี AC ตรง ๆ

def test_LNS_T01_loan_schema_exposes_required_fields_for_borrow_and_return_flow():
    book_copy = BookCopy(
        copy_id='CC-001',
        title_id='bk-clean-code',
        title='Clean Code',
        barcode='9780132350884',
        status='available',
        availability='available',
        last_loan_record_id='loan-001',
    )
    assert book_copy.title == 'Clean Code'
    assert book_copy.status == 'available'
    assert book_copy.barcode == '9780132350884'

    loan_record = LoanRecord(
        loan_id='loan-001',
        member_id='STD-1001',
        copy_id='CC-001',
        borrow_time='2026-11-12T09:00:00+07:00',
        due_date='2026-11-19',
        return_time=None,
        status='borrowed',
        overdue_days=0,
        penalty_amount=0,
    )
    assert loan_record.member_id == 'STD-1001'
    assert loan_record.due_date == '2026-11-19'
    assert loan_record.penalty_amount == 0

    notification_log = NotificationLog(
        notification_id='ntf-001',
        member_id='STD-1001',
        loan_id='loan-001',
        type='due_soon',
        scheduled_at='2026-11-17T08:00:00+07:00',
        sent_at=None,
        channel='email',
        status='scheduled',
    )
    assert notification_log.channel == 'email'
    assert notification_log.status == 'scheduled'

    audit_log = ReturnAuditLog(
        audit_id='audit-001',
        loan_id='loan-001',
        member_id='STD-1001',
        overdue_days=4,
        penalty_amount=12,
        processed_at='2026-11-26T10:00:00+07:00',
        actor='staff',
    )
    assert audit_log.overdue_days == 4
    assert audit_log.penalty_amount == 12
