from __future__ import annotations

from app.services.member_profile_seed import find_member

# IF-STD-01, IF-STD-02: ตรวจว่ารหัสบัตร/QR ถูกยืนยันจากระบบบัตรนักศึกษาภายนอกและไม่ใช่ข้อมูลที่ปลอมหรือไม่มีในระบบ
# การทำงานจริงจะเชื่อมต่อปลายทางภายนอกใน UC-02 แต่สำหรับเฟสนี้ใช้ seed data เป็น base validation เพื่อตรวจ flow


class ExternalIdentityVerificationError(Exception):
    """ไม่สามารถยืนยันตัวตนจากแหล่งภายนอกได้"""


def verify_external_member_id(member_id: str) -> bool:
    """IF-STD-01: ระบบภายนอกยอมรับเฉพาะ member_id ที่มีอยู่ในฐานข้อมูลสมาชิกของห้องสมุด"""

    return find_member(member_id) is not None
