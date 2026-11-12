import pytest

from app.models.facility_occupancy import build_seed_access_store
from app.services.access_service import AccessScanUnreadable, process_access_scan


def test_AC_ACC_03_unreadable_scan_is_rejected_without_logging():
    # Given เครื่องอ่านไม่สามารถอ่าน QR Code หรือบัตรนักศึกษาได้
    store = build_seed_access_store()

    # When รหัสสแกนว่างหรือรูปแบบ scan method ไม่ถูกต้อง
    with pytest.raises(AccessScanUnreadable):
        process_access_scan(store, '   ', 'qr')
    with pytest.raises(AccessScanUnreadable):
        process_access_scan(store, 'STD-1001', 'sms')

    # Then ระบบไม่สร้าง AccessEvent ใด ๆ และไม่ปรับจำนวนผู้ใช้บริการ
    assert len(store.events) == 0
    assert store.occupancy.current_occupancy == 128
