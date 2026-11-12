from __future__ import annotations

from dataclasses import dataclass

from app.config import ACCESS_MEMBER_SEED_DATA

# FR-ACC-01, FR-ACC-02, CON-ELG-01, DOM-PRV-01
# ข้อมูลสมาชิกและสถานะสิทธิ์ใช้เป็น seed สำหรับใช้งานจริงของ kiosk และ flow manual verification ต่อไป


@dataclass
class MemberProfile:
    """FR-ACC-01, FR-ACC-02: ข้อมูลผู้ใช้และสถานะสิทธิ์ที่ระบบใช้ตัดสินใจยืนยันตัวตน"""

    member_id: str
    member_type: str
    name: str
    eligibility_status: str
    status: str
    last_verified_at: str | None = None


def build_member_profiles() -> dict[str, MemberProfile]:
    """FR-ACC-01, FR-ACC-02: สร้าง dictionary ของ MemberProfile จาก config เพื่อใช้กับ access validation"""

    return {
        payload['member_id']: MemberProfile(
            member_id=payload['member_id'],
            member_type=payload['member_type'],
            name=payload['name'],
            eligibility_status=payload['eligibility_status'],
            status=payload['status'],
            last_verified_at=payload.get('last_verified_at'),
        )
        for payload in ACCESS_MEMBER_SEED_DATA
    }


def find_member(member_id: str) -> MemberProfile | None:
    """FR-ACC-02: หาข้อมูลสมาชิกจาก seed เพื่อใช้เป็นฐานในการตรวจสิทธิ์"""

    return build_member_profiles().get(member_id)


def is_eligible_for_access(member_id: str) -> bool:
    """CON-ELG-01: คืนค่า true เฉพาะเมื่อสิทธิ์เป็น eligible และ status ยัง active"""

    profile = find_member(member_id)
    return bool(profile and profile.eligibility_status == 'eligible' and profile.status == 'active')


def access_status_for_member(member_id: str) -> str:
    """FR-ACC-05: คืนสถานะที่แยกตามสาเหตุเพื่อให้ UI และ service แสดงผลได้ตรงตาม requirement"""

    profile = find_member(member_id)
    if profile is None:
        return 'not_found'
    if profile.eligibility_status == 'not_found':
        return 'not_found'
    if profile.eligibility_status == 'ineligible':
        return 'no_eligibility'
    if profile.eligibility_status == 'verification_failed':
        return 'verification_failed'
    return 'eligible'
