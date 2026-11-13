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


# ---------------------------------------------------------------------------
# 005-borrow-return: loan seed data and route shell
# ---------------------------------------------------------------------------

@dataclass
class LoanMemberProfile:
    """FR-LNS-01, FR-LNS-02, FR-LNS-07: ข้อมูลสมาชิกที่ใช้ใน workflow ยืม-คืน"""

    member_id: str
    member_type: str
    name: str
    email: str | None = None


LOAN_MEMBER_SEED_DATA = [
    {
        'member_id': 'STD-1001',
        'member_type': 'student',
        'name': 'นักศึกษาตัวอย่าง ก',
        'email': 'student.a@example.edu',
    },
    {
        'member_id': 'STF-2001',
        'member_type': 'staff',
        'name': 'บุคลากรตัวอย่าง',
        'email': 'staff@example.edu',
    },
    {
        'member_id': 'STD-1002',
        'member_type': 'student',
        'name': 'นักศึกษาตัวอย่าง ข',
        'email': 'student.b@example.edu',
    },
]


def build_loan_member_profiles() -> dict[str, LoanMemberProfile]:
    """FR-LNS-01, FR-LNS-07: สร้างรูปแบบสมาชิกสำหรับ seed data ในงานยืม-คืน"""

    return {
        payload['member_id']: LoanMemberProfile(
            member_id=payload['member_id'],
            member_type=payload['member_type'],
            name=payload['name'],
            email=payload.get('email'),
        )
        for payload in LOAN_MEMBER_SEED_DATA
    }


def find_loan_member(member_id: str) -> LoanMemberProfile | None:
    """FR-LNS-01, FR-LNS-07: คืนสมาชิกจาก seed data สำหรับ API shell"""

    return build_loan_member_profiles().get(member_id)


def loan_history_for_member(member_id: str) -> list[dict]:
    """FR-LNS-07: history ตัวอย่างสำหรับการทดสอบและ mock API ของผู้ยืม"""

    if member_id == 'STD-1001':
        return [
            {
                'loan_id': 'loan-001',
                'copy_id': 'CC-001',
                'borrow_date': '2026-11-12',
                'due_date': '2026-11-19',
                'return_date': '2026-11-19',
                'status': 'returned',
                'penalty_amount': 0,
            },
            {
                'loan_id': 'loan-002',
                'copy_id': 'CC-002',
                'borrow_date': '2026-11-20',
                'due_date': '2026-11-27',
                'return_date': None,
                'status': 'borrowed',
                'penalty_amount': 0,
            },
        ]
    return []
