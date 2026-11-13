from fastapi.testclient import TestClient

from app.api import loans as loan_api
from app.main import app
from app.models.book_copy import BookCopy
from app.models.loan_record import LoanRecord
from app.repositories.loan_repository import LoanRepository
from app.services.loan_service import LoanService


def _seed_repository(*, borrowed_copy_ids: list[str] | None = None, member_loans: int = 0):
    repository = LoanRepository(
        book_copies={
            'CC-101': BookCopy(
                copy_id='CC-101',
                title_id='bk-clean-code',
                title='Clean Code',
                barcode='BC-101',
                status='available',
                availability='available',
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
                loan_id=f'loan-{index}',
                member_id='STD-1001',
                copy_id=f'CC-{200 + index}',
                borrow_time='2026-11-12T09:00:00+07:00',
                due_date='2026-11-19',
                status='borrowed',
            )
            for index in range(1, member_loans + 1)
        ],
    )
    if borrowed_copy_ids:
        for copy_id in borrowed_copy_ids:
            repository.book_copies[copy_id].status = 'borrowed'
            repository.book_copies[copy_id].availability = 'borrowed'
    loan_api._loan_repository = repository
    loan_api._loan_service = LoanService(repository)
    return repository


def test_AC_LNS_01_loan_success_and_reminder():
    _seed_repository()
    client = TestClient(app)

    response = client.post('/api/loans/borrow', json={'member_id': 'STD-1001', 'barcode': 'BC-101', 'source': 'counter'})

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'approved'
    assert payload['due_date']
    assert payload['message']
    assert payload['notifications']
    assert any(item['channel'] == 'email' for item in payload['notifications'])


def test_AC_LNS_02_loan_denied_when_limit_exceeded():
    _seed_repository(member_loans=2)
    client = TestClient(app)

    response = client.post('/api/loans/borrow', json={'member_id': 'STD-1001', 'barcode': 'BC-102', 'source': 'counter'})

    assert response.status_code == 400
    payload = response.json()
    assert payload['status'] == 'borrow_limit_exceeded'
    assert 'ครบจำนวนหนังสือที่สามารถยืมได้' in payload['message']
