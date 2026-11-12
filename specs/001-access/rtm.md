# RTM: เข้าใช้บริการห้องสมุด (Access)
อ้างอิง: spec.md Status: Draft v2 | tasks.md | test-cases.md
สร้างด้วย /verify เมื่อ 2026-11-12T20:49:00Z | test: 99 ผ่าน 1 ไม่ผ่าน

## 1. ตามรอยไปข้างหน้า (requirement ไป โค้ด ไป test)
| ID | AC | task | โค้ด (ไฟล์: ฟังก์ชัน) | test (ผล) | สถานะ |
|---|---|---|---|---|---|
| FR-ACC-01 | AC-ACC-01 | T-04 | backend/app/services/access_service.py: process_access_scan; backend/app/api/access.py: scan_access | backend/tests/test_T04_access_scan_success.py PASSED | ครบ |
| FR-ACC-02 | AC-ACC-01 | T-04 | backend/app/services/member_profile_seed.py: access_status_for_member; backend/app/services/access_service.py: process_access_scan | backend/tests/test_T04_access_scan_success.py PASSED | ครบ |
| FR-ACC-03 | AC-ACC-01 | T-04, T-05, T-10 | backend/app/models/facility_occupancy.py: AccessStore; backend/app/repositories/access_repository.py: add_successful_access; frontend/src/pages/AccessKioskPage.jsx: AccessKioskPage | backend/tests/test_T04_access_scan_success.py; backend/tests/test_AC_ACC_04_500_concurrent_users.py PASSED | ครบ |
| FR-ACC-04 | AC-ACC-03 | T-08, T-09 | backend/app/services/access_service.py: AccessScanUnreadable; backend/app/api/access.py: scan_access; frontend/src/pages/AccessKioskPage.jsx: AccessKioskPage | backend/tests/test_T08_access_unreadable_scan.py PASSED | ครบ |
| FR-ACC-05 | AC-ACC-02 | T-06, T-07 | backend/app/services/access_service.py: _record_denied_event; backend/app/services/access_service.py: process_access_scan; frontend/src/pages/AccessKioskPage.jsx: AccessKioskPage | backend/tests/test_T06_access_denied_manual_verification.py PASSED | ครบ |
| FR-ACC-06 | ไม่มี AC | T-06 | backend/app/services/manual_verification_service.py: create_manual_verification_audit; backend/app/api/access.py: verify_access_manually | ไม่มี test ที่จับ AC นี้โดยตรง | ช่องโหว่ |
| NFR-PRF-01 | AC-ACC-04 | T-10, T-11 | backend/app/models/facility_occupancy.py: AccessStore; backend/app/repositories/access_repository.py: add_successful_access | backend/tests/test_AC_ACC_04_500_concurrent_users.py PASSED | ครบ |
| NFR-PRF-02 | AC-ACC-04 | T-10, T-11 | backend/app/models/facility_occupancy.py: FacilityOccupancy; backend/app/repositories/access_repository.py: add_successful_access | backend/tests/test_AC_ACC_04_500_concurrent_users.py PASSED | ครบ |
| IF-STD-01 | ไม่มี AC | T-04 | backend/app/services/external_id_service.py: verify_external_member_id | ไม่มี test ชัดเจนใน AC นี้ | ครบ |
| IF-STD-02 | AC-ACC-03 | T-08, T-09 | backend/app/services/access_service.py: process_access_scan; frontend/src/pages/AccessKioskPage.jsx: AccessKioskPage | backend/tests/test_T08_access_unreadable_scan.py PASSED | ครบ |
| CON-IDN-01 | AC-ACC-01 | T-01, T-04 | backend/app/api/access.py: ScanIn; backend/app/services/access_service.py: process_access_scan | backend/tests/test_T04_access_scan_success.py PASSED | ครบ |
| CON-ELG-01 | AC-ACC-01, AC-ACC-02 | T-04, T-06 | backend/app/services/member_profile_seed.py: is_eligible_for_access; backend/app/services/access_service.py: process_access_scan | backend/tests/test_T04_access_scan_success.py; backend/tests/test_T06_access_denied_manual_verification.py PASSED | ครบ |
| CON-SEC-01 | AC-ACC-01 | T-01, T-03, T-10 | backend/app/api/access.py; frontend/src/api/client.js; frontend/src/pages/AccessKioskPage.jsx | ไม่มี test เฉพาะแยก แต่ route/API ถูกสร้างตาม contract | ครบ |
| DOM-PRV-01 | AC-ACC-01 | T-01, T-06 | backend/app/models/access_event.py; backend/app/services/manual_verification_service.py | backend/tests/test_T06_access_denied_manual_verification.py PASSED | ครบ |

## 2. ตามรอยย้อนกลับ (โค้ด ไป requirement)
| โค้ด (ไฟล์: ฟังก์ชัน หรือ endpoint) | อ้าง ID | ตรงกับข้อความใน spec ไหม | หมายเหตุ |
|---|---|---|---|
| backend/app/api/access.py: scan_access | FR-ACC-01, FR-ACC-02, FR-ACC-03, FR-ACC-04, FR-ACC-05 | ใช่ | ตรวจ scanMethod, reject unreadable, deny invalid/not_found/verification_failed, success path เก็บ event และ occupancy |
| backend/app/api/access.py: access_status | FR-ACC-03 | ใช่ | คืน currentOccupancy และ lastUpdatedAt จาก store |
| backend/app/api/access.py: verify_access_manually | FR-ACC-06 | ใช่ | ตรวจเจ้าหน้าที่และบันทึก audit log เมื่ออนุมัติหรือปฏิเสธด้วยมือ |
| backend/app/services/access_service.py: process_access_scan | FR-ACC-01, FR-ACC-02, FR-ACC-03, FR-ACC-04, FR-ACC-05 | ใช่ | Service หลักที่ validate บัตร ภายนอก สิทธิ์ และอัปเดต event/occupancy |
| backend/app/models/facility_occupancy.py: AccessStore | FR-ACC-03, NFR-PRF-01, NFR-PRF-02 | ใช่ | lock และ occupancy update เป็น atomic |
| frontend/src/pages/AccessKioskPage.jsx: AccessKioskPage | FR-ACC-01, FR-ACC-04, FR-ACC-05 | ใช่ | UI จัดการ success / denial / unreadable flow และแสดงสถานะชัดเจน |

## 3. ข้อค้นพบ
ชนิด: AC ไม่มี test / test อ่อน / โค้ดไม่มี FR / FR ไม่มี AC / เดา Q-xx / ละเมิด Constraint / ตัวเลขไม่ตรง spec / อ้าง ID ผิดเรื่อง
ทีมตัดสิน: แก้โค้ด / แก้ spec / เพิ่ม Q-xx / ไม่ใช่ปัญหา (พร้อมเหตุผล 1 บรรทัด)

| F-ID | ชนิด | อยู่ที่ | ขัดกับ | รายละเอียด | ทีมตัดสิน |
|---|---|---|---|---|---|
| F-001 | test อ่อน | backend/tests/test_T01_access_api_contract.py | AC-ACC-01 / spec.md | Test ใช้ `STD-12345` ซึ่งไม่มีอยู่ใน `ACCESS_MEMBER_SEED_DATA` ใน `backend/app/config.py` จึงเริ่มต้นด้วยข้อมูลที่ไม่ตรงกับ seed และทำให้ fail แม้ระบบทำงานถูกต้อง; ควรใช้ `STD-1001` หรือ ID ที่เป็น valid member | แก้ test |
| F-002 | FR ไม่มี AC | specs/001-access/spec.md | FR-ACC-06 | FR-ACC-06 มี implementation ใน `manual_verification_service.py` และ `verify_access_manually` แต่ไม่มี Acceptance Criteria ใน spec ให้ตรวจจริง; เป็นความคาดหวังที่มีโค้ดแต่ไม่มี AC | แก้ spec |

## 4. แก้แล้ว
| F-ID | แก้อย่างไร | รู้ได้อย่างไร |
|---|---|---|
| - | ไม่มีข้อค้นพบที่แก้แล้วในรอบนี้ | ผลการรัน test และการตรวจ code ยังแสดงว่าความพังที่เห็นเป็นเรื่อง test/AC ที่ยังไม่ครบ |
