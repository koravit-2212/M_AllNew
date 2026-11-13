from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.api import loans as loan_api
from app.main import app
from app.models.book_copy import BookCopy
from app.models.loan_record import LoanRecord
from app.repositories.loan_repository import LoanRepository
from app.services.loan_service import LoanService


def _seed_repository():
    today = date.today()
    repository = LoanRepository(
        book_copies={
            'CC-101': BookCopy(
                copy_id='CC-101',
                title_id='bk-clean-code',
                title='Clean Code',
                barcode='BC-101',
                status='borrowed',
                availability='borrowed',
            ),
            'CC-102': BookCopy(
                copy_id='CC-102',
                title_id='bk-clean-code',
                title='Clean Code',
                barcode='BC-102',
                status='available',
                availability='available',
            ),
        },
        loan_records=[
            LoanRecord(
                loan_id='loan-101',
                member_id='STD-1001',
                copy_id='CC-101',
                borrow_time=(today - timedelta(days=20)).isoformat(),
                due_date=(today - timedelta(days=10)).isoformat(),
                return_time=(today - timedelta(days=8)).isoformat(),
                status='returned',
                overdue_days=2,
                penalty_amount=6,
            ),
            LoanRecord(
                loan_id='loan-102',
                member_id='STD-1001',
                copy_id='CC-102',
                borrow_time=(today - timedelta(days=3)).isoformat(),
                due_date=(today + timedelta(days=11)).isoformat(),
                return_time=None,
                status='borrowed',
                overdue_days=0,
                penalty_amount=0,
            ),
        ],
    )
    loan_api._loan_repository = repository
    loan_api._loan_service = LoanService(repository)
    return repository


def test_AC_LNS_04_member_history_view():
    _seed_repository()
    client = TestClient(app)

    response = client.get('/api/loans/history/STD-1001')

    assert response.status_code == 200
    payload = response.json()
    assert payload['member_id'] == 'STD-1001'
    assert len(payload['history']) == 2

    returned_record = payload['history'][0]
    assert returned_record['loan_id'] == 'loan-101'
    assert returned_record['status'] == 'returned'
    assert returned_record['return_date'] == (date.today() - timedelta(days=8)).isoformat()
    assert returned_record['penalty_amount'] == 6

    active_record = payload['history'][1]
    assert active_record['loan_id'] == 'loan-102'
    assert active_record['status'] == 'borrowed'
    assert active_record['return_date'] is None
    assert active_record['penalty_amount'] == 0
