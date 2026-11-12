import pytest

from _prt_helpers import PrintEnv
from app.config import PRINT_RATE_PER_PAGE_BAHT

# test จาก specs/006-printing/test-cases.md (AC-PRT-02) ห้ามแก้ให้ผ่าน


@pytest.fixture
def env():
    e = PrintEnv()
    yield e
    e.close()


def test_TC_PRT_02_1_submit_sends_and_records(env):
    # Given เครื่องพิมพ์พร้อมใช้งาน เลือก report.pdf ขาว-ดำ 12 หน้า 2 ชุด
    printer = env.store.printers[0]
    assert printer.is_ready
    file_id = env.upload('report.pdf').json()['file_id']

    # When นักศึกษายืนยันการพิมพ์
    submitted = env.submit(file_id, 12, 2, 'BW')
    job = env.client.get(f"/api/print/jobs/{submitted.json()['printjob_id']}").json()

    # Then (1) spooler ได้รับงาน 1 งาน 12 หน้า 2 ชุด ขาว-ดำ ส่งไปเครื่องที่พร้อม
    assert len(env.store.spooler.received_jobs) == 1
    sent = env.store.spooler.received_jobs[0]
    assert (sent['pages'], sent['copies'], sent['color_mode'], sent['printer_id']) == (12, 2, 'BW', printer.printer_id)
    # (2) บันทึกการใช้บริการ สถานะ sent รวม 24 หน้า ค่าใช้บริการตามอัตรา อ่านกลับได้
    assert submitted.status_code == 201
    assert job['status'] == 'sent'
    assert job['total_pages'] == 24
    assert job['total_cost'] == 24 * PRINT_RATE_PER_PAGE_BAHT['BW']
    assert job['filename'] == 'report.pdf'
    # (3) หน้าจอ ตรวจด้วย vitest TC-PRT-02-1.test.jsx


def test_TC_PRT_02_2_single_page_single_copy(env):
    # Given เครื่องพิมพ์พร้อม เลือกไฟล์ที่รองรับ
    file_id = env.upload().json()['file_id']

    # When ยืนยันการพิมพ์ 1 หน้า 1 ชุด
    submitted = env.submit(file_id, 1, 1)

    # Then (1) spooler ได้รับงาน 1 หน้า 1 ชุด
    assert [(j['pages'], j['copies']) for j in env.store.spooler.received_jobs] == [(1, 1)]
    # (2) บันทึกงาน รวม 1 หน้า
    assert submitted.json()['total_pages'] == 1


def test_TC_PRT_02_3_unknown_file_not_sent(env):
    # Given เครื่องพิมพ์พร้อม แต่ไม่มีไฟล์ที่รองรับ (file_id ไม่มีในระบบ)
    # When ยืนยันการพิมพ์
    response = env.submit('FILE-9999', 3, 1)

    # Then (1) ไม่รับงาน
    assert response.status_code == 404
    # (2) spooler ไม่ได้รับงาน และไม่มีงานถูกบันทึก
    assert env.store.spooler.received_jobs == []
    assert env.store.jobs == {}
