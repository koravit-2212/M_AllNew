import pytest

from _prt_helpers import PrintEnv
from app.config import PRINT_ALLOWED_EXTENSIONS, PRINT_MAX_FILE_SIZE_BYTES

# test จาก specs/006-printing/test-cases.md (AC-PRT-04) ห้ามแก้ให้ผ่าน


@pytest.fixture
def env():
    e = PrintEnv()
    yield e
    e.close()


def test_TC_PRT_04_1_exe_rejected(env):
    # Given ไฟล์ setup.exe
    # When นักศึกษาเลือกไฟล์
    response = env.upload('setup.exe', 1000)

    # Then (1) แจ้งเตือน "ไม่รองรับไฟล์ชนิดนี้" พร้อมชนิดที่รองรับ
    assert response.status_code == 415
    assert response.json()['detail']['message'] == 'ไม่รองรับไฟล์ชนิดนี้'
    assert response.json()['detail']['allowed_extensions'] == list(PRINT_ALLOWED_EXTENSIONS)
    # (2) ไม่ได้ file_id และไม่มีไฟล์ถูกบันทึก
    assert 'file_id' not in response.json()
    assert env.store.files == {}
    # (3) หน้าจอ ตรวจด้วย vitest TC-PRT-04-1.test.jsx


def test_TC_PRT_04_2_size_limit_50mb(env):
    # Given ไฟล์ PDF ขนาด 50 MB พอดี และ 50 MB + 1 byte
    # When นักศึกษาเลือกไฟล์ทีละไฟล์
    exact = env.upload('exact.pdf', PRINT_MAX_FILE_SIZE_BYTES)
    over = env.upload('over.pdf', PRINT_MAX_FILE_SIZE_BYTES + 1)

    # Then (1) 50 MB พอดีรับได้
    assert exact.status_code == 201
    # (2) เกิน 50 MB แจ้งเตือนและไม่บันทึก
    assert over.status_code == 415
    assert over.json()['detail']['message'] == 'ไม่รองรับไฟล์ชนิดนี้'
    assert [f.filename for f in env.store.files.values()] == ['exact.pdf']


def test_TC_PRT_04_3_uppercase_ext_and_no_ext(env):
    # Given ไฟล์ REPORT.PDF และไฟล์ที่ไม่มีนามสกุล
    # When นักศึกษาเลือกไฟล์ทีละไฟล์
    upper = env.upload('REPORT.PDF', 100)
    no_ext = env.upload('README', 100)

    # Then (1) REPORT.PDF รับได้
    assert upper.status_code == 201
    # (2) ไม่มีนามสกุลแจ้งเตือนและไม่บันทึก
    assert no_ext.status_code == 415
    assert len(env.store.files) == 1


def test_TC_PRT_04_4_supported_docx_ok(env):
    # Given ไฟล์ notes.docx
    # When นักศึกษาเลือกไฟล์
    response = env.upload('notes.docx', 2000)

    # Then (1) ไม่มีคำเตือน ได้ file_id
    assert response.status_code == 201
    assert 'ไม่รองรับไฟล์ชนิดนี้' not in response.text
    assert response.json()['file_id'] in env.store.files
    # (2) หน้าจอ ตรวจด้วย vitest TC-PRT-04-4.test.jsx
