import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from app.config import ACCESS_CONCURRENT_REQUEST_LIMIT, ACCESS_VALIDATION_TARGET_SECONDS
from app.models.facility_occupancy import build_seed_access_store
from app.services import access_service as access_service_module


def test_AC_ACC_04_500_concurrent_users(monkeypatch):
    # Given ผู้ใช้งานพร้อมกัน 500 คน
    store = build_seed_access_store()
    initial_occupancy = store.occupancy.current_occupancy

    def fake_verify_external_member_id(member_id):
        return True

    def fake_find_member(member_id):
        return SimpleNamespace(name=f'นักศึกษาตัวอย่าง {member_id}')

    def fake_access_status_for_member(member_id):
        return 'eligible'

    def fake_is_eligible_for_access(member_id):
        return True

    monkeypatch.setattr(access_service_module, 'verify_external_member_id', fake_verify_external_member_id)
    monkeypatch.setattr(access_service_module, 'find_member', fake_find_member)
    monkeypatch.setattr(access_service_module, 'access_status_for_member', fake_access_status_for_member)
    monkeypatch.setattr(access_service_module, 'is_eligible_for_access', fake_is_eligible_for_access)

    # When แต่ละคนสแกนเข้าใช้บริการพร้อมกัน
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [
            executor.submit(access_service_module.process_access_scan, store, f'STD-{index:04d}', 'qr')
            for index in range(ACCESS_CONCURRENT_REQUEST_LIMIT)
        ]
        results = [future.result() for future in futures]
    elapsed = time.perf_counter() - start

    # Then ระบบยังคงให้บริการได้และอัปเดตจำนวนผู้ใช้บริการแบบ atomic
    assert len(results) == ACCESS_CONCURRENT_REQUEST_LIMIT
    assert all(result['allowed'] is True for result in results)
    assert store.occupancy.current_occupancy == initial_occupancy + ACCESS_CONCURRENT_REQUEST_LIMIT
    assert len(store.events) == ACCESS_CONCURRENT_REQUEST_LIMIT
    assert elapsed < ACCESS_VALIDATION_TARGET_SECONDS
