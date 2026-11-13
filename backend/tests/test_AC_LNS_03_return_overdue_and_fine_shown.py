from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.api import loans as loan_api
from app.main import app
from app.models.book_copy import BookCopy
from app.models.loan_record import LoanRecord
from app.repositories.loan_repository import LoanRepository
from app.services.loan_service import LoanService


def _seed_repository(*, overdue_days: int = 4):
    overdue_date = (date.today() - timedelta(days=overdue_days)).isoformat()
    repository = LoanRepository(
        book_copies={
            'CC-201': BookCopy(
                copy_id='CC-201',
                title_id='bk-clean-code',
                title='Clean Code',
                barcode='BC-201',
                status='borrowed',
                availability='borrowed',
            )
        },
        loan_records=[
            LoanRecord(
                loan_id='loan-201',
                member_id='STD-1001',
                copy_id='CC-201',
                borrow_time='2026-11-01T09:00:00+07:00',
                due_date=overdue_date,
                status='borrowed',
                overdue_days=0,
                penalty_amount=0,
            )
        ],
    )
    loan_api._loan_repository = repository
    loan_api._loan_service = LoanService(repository)
    return repository


def test_AC_LNS_03_return_overdue_and_fine_shown():
    _seed_repository(overdue_days=4)
    client = TestClient(app)

    response = client.post('/api/loans/return', json={'member_id': 'STD-1001', 'barcode': 'BC-201'})

    assert response.status_code == 200
    payload = response.json()
    assert payload['loan_id'] == 'loan-201'
    assert payload['return_status'] == 'returned'
    assert payload['overdue_days'] == 4
    assert payload['penalty_amount'] == 12
    assert 'คืนสำเร็จ' in payload['message']
    assert payload['audit_log']
