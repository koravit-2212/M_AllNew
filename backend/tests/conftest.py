from datetime import datetime as real_datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.api.equipment import get_equipment_store
from app.main import app
from app.models.equipment import Student, build_seed_equipment_store
from app.services import equipment_service


# fixture ร่วมของ test ที่มาจาก specs/007-equipment/test-cases.md


@pytest.fixture
def eqp_store():
    """ที่เก็บอุปกรณ์ใหม่ต่อ test แทนที่ของจริงผ่าน dependency_overrides"""

    store = build_seed_equipment_store()
    app.dependency_overrides[get_equipment_store] = lambda: store
    yield store
    app.dependency_overrides.pop(get_equipment_store, None)


@pytest.fixture
def eqp_client(eqp_store):
    return TestClient(app)


@pytest.fixture
def student_clear(eqp_store):
    """นักศึกษาที่ไม่มีรายการค้างคืน"""

    return next(s for s in eqp_store.students.values() if not s.has_outstanding)


@pytest.fixture
def student_outstanding(eqp_store):
    """นักศึกษาที่มีรายการค้างคืน"""

    return next(s for s in eqp_store.students.values() if s.has_outstanding)


@pytest.fixture
def add_student(eqp_store):
    def _add(student_id, outstanding_items=None):
        student = Student(student_id=student_id, name=f'นักศึกษาทดสอบ {student_id}', outstanding_items=outstanding_items or [])
        eqp_store.students[student_id] = student
        return student

    return _add


@pytest.fixture
def type_id(eqp_store):
    """หา equipment_type_id จากชื่อประเภท"""

    def _find(name):
        return next(e.equipment_type_id for e in eqp_store.equipment_types.values() if e.name == name)

    return _find


@pytest.fixture
def fixed_now(monkeypatch):
    """ตั้งเวลาปัจจุบันของระบบ (รับเวลาตามเขต Asia/Bangkok)"""

    def _set(year, month, day, hour=10, minute=0):
        fixed = real_datetime(year, month, day, hour, minute, tzinfo=ZoneInfo('Asia/Bangkok'))

        class FixedDatetime(real_datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed.astimezone(tz) if tz else fixed.replace(tzinfo=None)

        monkeypatch.setattr(equipment_service, 'datetime', FixedDatetime)
        return fixed

    return _set


def create_request(client, student_id, equipment_type_id, quantity=1):
    return client.post(
        '/api/loan-requests',
        json={'student_id': student_id, 'equipment_type_id': equipment_type_id, 'quantity': quantity},
    )
