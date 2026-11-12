import pytest

from _prt_helpers import PrintEnv
from app.config import PRINT_RATE_PER_PAGE_BAHT

# test จาก specs/006-printing/test-cases.md (AC-PRT-01) ห้ามแก้ให้ผ่าน


@pytest.fixture
def env():
    e = PrintEnv()
    yield e
    e.close()


def test_TC_PRT_01_1_bw_cost_preview(env):
    # Given นักศึกษาเลือกไฟล์ report.pdf และเลือกชนิดขาว-ดำ
    file_id = env.upload('report.pdf').json()['file_id']

    # When กำหนดจำนวนหน้า 12 และจำนวนชุด 2
    payload = env.options(file_id, 12, 2, 'BW').json()

    # Then (1) แสดงตัวเลือกชนิดการพิมพ์ ขาว-ดำ และสี
    assert {m['label'] for m in payload['allowed_color_modes']} == {'ขาว-ดำ', 'สี'}
    # (2) จำนวนหน้ารวม 24
    assert payload['total_pages'] == 24
    # (3) ค่าใช้บริการ = 24 × อัตราขาว-ดำ
    assert payload['estimated_cost'] == 24 * PRINT_RATE_PER_PAGE_BAHT['BW']
    # (4) ยังไม่มีงานพิมพ์ถูกส่งหรือบันทึก
    assert env.store.jobs == {}
    assert env.store.spooler.received_jobs == []
    # (5) หน้าจอ ตรวจด้วย vitest TC-PRT-01-1.test.jsx


def test_TC_PRT_01_2_color_cost_preview(env):
    # Given เลือกไฟล์ที่รองรับ และเลือกชนิดสี
    file_id = env.upload().json()['file_id']

    # When กำหนดจำนวนหน้า 12 และจำนวนชุด 2
    payload = env.options(file_id, 12, 2, 'Color').json()

    # Then (1) ค่าใช้บริการ = 24 × อัตราสี
    assert payload['estimated_cost'] == 24 * PRINT_RATE_PER_PAGE_BAHT['Color']
    # (2) หน้าจอ ตรวจด้วย vitest TC-PRT-01-2.test.jsx


def test_TC_PRT_01_3_min_pages_and_zero_rejected(env):
    # Given เลือกไฟล์ที่รองรับแล้ว
    file_id = env.upload().json()['file_id']

    # When กำหนด 1 หน้า 1 ชุด และลอง 0 หน้า
    one = env.options(file_id, 1, 1, 'BW')
    zero = env.options(file_id, 0, 1, 'BW')

    # Then (1) รวม 1 หน้า ค่าใช้บริการเท่าอัตรา 1 หน้า
    assert one.json()['total_pages'] == 1
    assert one.json()['estimated_cost'] == PRINT_RATE_PER_PAGE_BAHT['BW']
    # (2) 0 หน้า ไม่คำนวณ
    assert zero.status_code == 422
    assert 'estimated_cost' not in zero.text


def test_TC_PRT_01_4_unsupported_file_no_cost(env):
    # Given นักศึกษาเลือกไฟล์ที่ไม่รองรับ
    uploaded = env.upload('virus.exe')

    # When กำหนดจำนวนหน้าและจำนวนชุด (ไม่มี file_id จึงใช้ค่าที่เดาไม่ได้)
    options = env.options('FILE-0001', 12, 2)

    # Then (1) ไม่ได้ file_id ขอค่าใช้บริการไม่ได้
    assert 'file_id' not in uploaded.json()
    assert options.status_code == 404
    # (2) ไม่มีไฟล์ถูกบันทึก
    assert env.store.files == {}
