import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from app.config import ACCESS_CONCURRENT_REQUEST_LIMIT
from app.models.facility_occupancy import build_seed_access_store
from app.services import access_service as access_service_module


def run_load_test():
    store = build_seed_access_store()

    def fake_verify_external_member_id(member_id):
        return True

    def fake_find_member(member_id):
        return SimpleNamespace(name=f'นักศึกษาตัวอย่าง {member_id}')

    def fake_access_status_for_member(member_id):
        return 'eligible'

    def fake_is_eligible_for_access(member_id):
        return True

    access_service_module.verify_external_member_id = fake_verify_external_member_id
    access_service_module.find_member = fake_find_member
    access_service_module.access_status_for_member = fake_access_status_for_member
    access_service_module.is_eligible_for_access = fake_is_eligible_for_access

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [
            executor.submit(access_service_module.process_access_scan, store, f'STD-{index:04d}', 'qr')
            for index in range(ACCESS_CONCURRENT_REQUEST_LIMIT)
        ]
        results = [future.result() for future in futures]
    elapsed = time.perf_counter() - start

    print({
        'requests': ACCESS_CONCURRENT_REQUEST_LIMIT,
        'succeeded': len(results),
        'final_occupancy': store.occupancy.current_occupancy,
        'elapsed_seconds': round(elapsed, 4),
    })


if __name__ == '__main__':
    run_load_test()
