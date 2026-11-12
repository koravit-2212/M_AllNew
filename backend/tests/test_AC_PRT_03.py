import pytest

from _prt_helpers import PrintEnv

# test จาก specs/006-printing/test-cases.md (AC-PRT-03) ห้ามแก้ให้ผ่าน


@pytest.fixture
def env():
    e = PrintEnv()
    yield e
    e.close()


def test_TC_PRT_03_1_offline_not_sent(env):
    # Given เครื่องพิมพ์สถานะ offline และเลือกไฟล์ที่รองรับแล้ว
    for printer in env.store.printers:
        printer.status = 'offline'
    file_id = env.upload().json()['file_id']

    # When นักศึกษายืนยันการพิมพ์
    response = env.submit(file_id, 5, 1)
    status = env.client.get('/api/printers/status').json()['printers']

    # Then (1) แจ้งเตือน "เครื่องพิมพ์ไม่พร้อมใช้งาน"
    assert response.status_code == 409
    assert response.json()['detail'] == 'เครื่องพิมพ์ไม่พร้อมใช้งาน'
    # (2) spooler ไม่ได้รับงาน และไม่มีงานถูกบันทึก
    assert env.store.spooler.received_jobs == []
    assert env.store.jobs == {}
    # (3) สถานะเครื่องพิมพ์แสดง offline
    assert all(p['status'] == 'offline' and p['ready'] is False for p in status)
    # (4) หน้าจอ ตรวจด้วย vitest TC-PRT-03-1.test.jsx


def test_TC_PRT_03_2_error_then_ready(env):
    # Given เครื่องพิมพ์สถานะ error
    env.store.printers[0].status = 'error'
    file_id = env.upload().json()['file_id']

    # When ยืนยันการพิมพ์ แล้วเครื่องกลับมาพร้อม แล้วยืนยันอีกครั้ง
    first = env.submit(file_id, 2, 1)
    env.store.printers[0].status = 'ready'
    second = env.submit(file_id, 2, 1)

    # Then (1) ครั้งแรกแจ้งเตือนและไม่ส่ง
    assert first.status_code == 409
    # (2) ครั้งที่สองส่งได้ spooler ได้รับงาน 1 งาน
    assert second.status_code == 201
    assert len(env.store.spooler.received_jobs) == 1


def test_TC_PRT_03_3_ready_printer_sends(env):
    # Given เครื่องพิมพ์พร้อมใช้งาน
    file_id = env.upload().json()['file_id']

    # When ยืนยันการพิมพ์
    response = env.submit(file_id, 2, 1)

    # Then (1) ไม่มีข้อความเครื่องพิมพ์ไม่พร้อม
    assert 'เครื่องพิมพ์ไม่พร้อมใช้งาน' not in response.text
    # (2) ส่งงานสำเร็จ
    assert response.status_code == 201
    assert response.json()['status'] == 'sent'
