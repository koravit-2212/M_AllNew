import threading
from datetime import date

from fastapi.testclient import TestClient

from app.api.spaces import get_space_store
from app.main import app
from app.models.space import build_seed_space_store
from app.services import reservation_service
from app.services.reservation_service import SlotUnavailable, create_reservation


# T-09 (NFR-REL-03, CON-CONC-01) ตรวจด้วย AC-BKG-04


def _book_concurrently(store, slot, user_ids):
    """เรียก service จากหลาย thread ให้เริ่มพร้อมกันด้วย barrier คืนผลเป็น 'ok' หรือ 'unavailable'"""

    barrier = threading.Barrier(len(user_ids))
    results = [None] * len(user_ids)

    def book(index, user_id):
        barrier.wait()
        try:
            create_reservation(store, user_id, slot.space_id, slot.date, slot.start_time, slot.end_time)
            results[index] = 'ok'
        except SlotUnavailable:
            results[index] = 'unavailable'

    threads = [threading.Thread(target=book, args=(i, u)) for i, u in enumerate(user_ids)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def _slow_check(monkeypatch):
    # ทำให้ช่วงระหว่าง "ตรวจว่าง" กับ "บันทึก" ยาวขึ้น ถ้าไม่มี lock (CON-CONC-01) จะจองซ้อนได้แน่นอน
    original = reservation_service._slot_taken

    def slow(*args, **kwargs):
        result = original(*args, **kwargs)
        threading.Event().wait(0.05)
        return result

    monkeypatch.setattr(reservation_service, '_slot_taken', slow)


def test_AC_BKG_04_concurrent_booking_prevented(monkeypatch):
    # Given มีผู้ใช้สองคนพยายามจองพื้นที่และเวลาเดียวกันพร้อมกัน
    store = build_seed_space_store(date(2026, 11, 13))
    slot = store.slots_for(next(s for s in store.spaces if s.is_open).space_id)[0]
    _slow_check(monkeypatch)

    # When ทั้งสองยืนยันเกือบพร้อมกัน
    results = _book_concurrently(store, slot, ['64000001', 'ST-1001'])

    # Then ระบบอนุญาตให้จองสำเร็จเพียงรายการเดียว และอีกรายการได้รับแจ้งว่าพื้นที่ไม่ว่าง
    assert sorted(results) == ['ok', 'unavailable']
    assert len(store.reservations) == 1


def test_AC_BKG_04_many_concurrent_users_only_one_succeeds(monkeypatch):
    store = build_seed_space_store(date(2026, 11, 13))
    slot = store.slots_for(next(s for s in store.spaces if s.is_open).space_id)[2]
    _slow_check(monkeypatch)

    results = _book_concurrently(store, slot, ['64000001', 'ST-1001'] * 4)

    assert results.count('ok') == 1
    assert results.count('unavailable') == 7
    assert len(store.reservations) == 1


def test_AC_BKG_04_second_request_gets_unavailable_message_via_api():
    # ผ่าน API: คำขอที่มาทีหลังได้ข้อความพื้นที่ไม่ว่าง
    store = build_seed_space_store(date(2026, 11, 13))
    slot = store.slots_for(next(s for s in store.spaces if s.is_open).space_id)[3]
    body = {'spaceId': slot.space_id, 'date': slot.date, 'startTime': slot.start_time, 'endTime': slot.end_time}
    app.dependency_overrides[get_space_store] = lambda: store
    try:
        client = TestClient(app)
        first = client.post('/api/reservations', json={**body, 'userId': '64000001'})
        second = client.post('/api/reservations', json={**body, 'userId': 'ST-1001'})
    finally:
        app.dependency_overrides.clear()

    assert (first.status_code, second.status_code) == (201, 409)
    assert second.json()['detail'] == 'พื้นที่ไม่ว่างในช่วงเวลานี้'
