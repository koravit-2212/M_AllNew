import threading
from datetime import date

from app.models.space import build_seed_space_store
from app.services import reservation_service
from app.services.reservation_service import SlotUnavailable, create_reservation

# test จาก specs/004-reserve/test-cases.md (AC-BKG-04) ห้ามแก้ให้ผ่าน

DAY = date(2026, 11, 13)


def _slow_check(monkeypatch):
    # หน่วงเวลาระหว่าง "ตรวจว่าง" กับ "บันทึก" ให้เกิดการแย่งกันจริง
    original = reservation_service._slot_taken

    def slow(*args, **kwargs):
        result = original(*args, **kwargs)
        threading.Event().wait(0.05)
        return result

    monkeypatch.setattr(reservation_service, '_slot_taken', slow)


def _concurrent(store, jobs):
    """jobs = [(user_id, slot)] เริ่มพร้อมกันด้วย barrier คืน 'ok' / 'unavailable' ตามลำดับ"""

    barrier = threading.Barrier(len(jobs))
    results = [None] * len(jobs)

    def run(i, user_id, slot):
        barrier.wait()
        try:
            create_reservation(store, user_id, slot.space_id, slot.date, slot.start_time, slot.end_time)
            results[i] = 'ok'
        except SlotUnavailable:
            results[i] = 'unavailable'

    threads = [threading.Thread(target=run, args=(i, u, s)) for i, (u, s) in enumerate(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_TC_BKG_04_1_two_concurrent_only_one_succeeds(monkeypatch):
    # Given ผู้ใช้ 2 คนที่มีสิทธิ์จองพื้นที่และช่วงเวลาเดียวกันที่ยังว่าง
    store = build_seed_space_store(DAY)
    slot = store.slots_for(next(s.space_id for s in store.spaces if s.is_open))[0]
    _slow_check(monkeypatch)

    # When ทั้งสองยืนยันเกือบพร้อมกัน
    results = _concurrent(store, [('64000001', slot), ('ST-1001', slot)])

    # Then (1) สำเร็จเพียง 1 รายการ
    assert results.count('ok') == 1
    # (2) อีกรายการได้รับแจ้งว่าพื้นที่ไม่ว่าง
    assert results.count('unavailable') == 1
    # (3) มีรายการจองของช่วงนั้นเพียง 1 รายการ
    assert [r.slot_id for r in store.reservations] == [slot.slot_id]


def test_TC_BKG_04_2_eight_concurrent_only_one_succeeds(monkeypatch):
    # Given ผู้ใช้ 8 คนจองพื้นที่และช่วงเวลาเดียวกันที่ยังว่าง
    store = build_seed_space_store(DAY)
    slot = store.slots_for(next(s.space_id for s in store.spaces if s.is_open))[1]
    _slow_check(monkeypatch)

    # When ทั้ง 8 คนยืนยันพร้อมกัน
    results = _concurrent(store, [('64000001' if i % 2 else 'ST-1001', slot) for i in range(8)])

    # Then (1) สำเร็จ 1 อีก 7 ไม่ว่าง
    assert results.count('ok') == 1
    assert results.count('unavailable') == 7
    # (2) มีรายการจองเพียง 1 รายการ
    assert len(store.reservations) == 1


def test_TC_BKG_04_3_concurrent_different_slots_both_succeed(monkeypatch):
    # Given ผู้ใช้ 2 คนจองช่วงเวลาต่างกัน
    store = build_seed_space_store(DAY)
    first, second = store.slots_for(next(s.space_id for s in store.spaces if s.is_open))[:2]
    _slow_check(monkeypatch)

    # When ทั้งสองยืนยันพร้อมกัน
    results = _concurrent(store, [('64000001', first), ('ST-1001', second)])

    # Then (1) สำเร็จทั้ง 2 รายการ
    assert results == ['ok', 'ok']
    # (2) มีรายการจอง 2 รายการ คนละช่วงเวลา
    assert sorted(r.slot_id for r in store.reservations) == sorted([first.slot_id, second.slot_id])
