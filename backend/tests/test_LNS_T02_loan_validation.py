from app.models.book_copy import BookCopy
from app.models.loan_record import LoanRecord
from app.repositories.loan_repository import LoanRepository
from app.services.loan_service import LoanService


# T-02 (FR-LNS-02, FR-LNS-04, CON-LNS-01) ตรวจเชิง logic ให้ API/หน้าจอรู้เหตุผลชัดเจน

def test_LNS_T02_loan_service_rejects_limit_exceeded_and_borrowed_copy():
    repository = LoanRepository(
        book_copies={
            'CC-001': BookCopy(
                copy_id='CC-001',
                title_id='bk-clean-code',
                title='Clean Code',
                barcode='9780132350884',
                status='borrowed',
                availability='borrowed',
                last_loan_record_id='loan-001',
            ),
        },
        loan_records=[
            LoanRecord(
                loan_id='loan-001',
                member_id='STD-1001',
                copy_id='CC-002',
                borrow_time='2026-11-12T09:00:00+07:00',
                due_date='2026-11-19',
                return_time=None,
                status='borrowed',
                overdue_days=0,
                penalty_amount=0,
            ),
            LoanRecord(
                loan_id='loan-002',
                member_id='STD-1001',
                copy_id='CC-003',
                borrow_time='2026-11-12T09:00:00+07:00',
                due_date='2026-11-19',
                return_time=None,
                status='borrowed',
                overdue_days=0,
                penalty_amount=0,
            ),
        ],
    )
    service = LoanService(repository)

    copied_borrowed = service.validate_loan('STD-1002', 'CC-001', max_books_per_member=2)
    assert copied_borrowed['allowed'] is False
    assert copied_borrowed['status'] == 'copy_unavailable'
    assert 'ถูกยืมอยู่แล้ว' in copied_borrowed['message']

    limit_exceeded = service.validate_loan('STD-1001', 'CC-004', max_books_per_member=2)
    assert limit_exceeded['allowed'] is False
    assert limit_exceeded['status'] == 'borrow_limit_exceeded'
    assert 'ครบจำนวนหนังสือที่สามารถยืมได้' in limit_exceeded['message']

    allowed = service.validate_loan('STD-1003', 'CC-004', max_books_per_member=2)
    assert allowed['allowed'] is True
    assert allowed['status'] == 'eligible'
