from app.services.member_profile_seed import access_status_for_member, build_member_profiles, is_eligible_for_access


def test_T02_access_member_seed_has_valid_and_invalid_profiles():
    # Given มีข้อมูล seed สำหรับผู้ใช้ที่มีสิทธิ์และไม่มีสิทธิ์
    profiles = build_member_profiles()

    # When เรียกตรวจสิทธิ์และสถานะตามสาเหตุ
    eligible = is_eligible_for_access('STD-1001')
    no_eligibility = access_status_for_member('STD-1002')
    not_found = access_status_for_member('UNKNOWN-999')
    verification_failed = access_status_for_member('STD-1003')

    # Then ระบบต้องแยกสถานะชัดเจนเพื่อใช้ใน AC-ACC-01 และ AC-ACC-02
    assert eligible is True
    assert profiles['STD-1001'].member_type == 'student'
    assert no_eligibility == 'no_eligibility'
    assert not_found == 'not_found'
    assert verification_failed == 'verification_failed'
    assert 'STF-2001' in profiles
