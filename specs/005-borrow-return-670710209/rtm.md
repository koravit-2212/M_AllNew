# RTM: ยืม-คืนหนังสือ (Book Loan / Return)
อ้างอิง: spec.md Draft v2 | tasks.md | test-cases.md
สร้างด้วย /verify เมื่อ 2026-11-13 05:45 | test: 167 ผ่าน 1 ไม่ผ่าน

## 1. ตามรอยไปข้างหน้า (requirement ไป โค้ด ไป test)
| ID | AC | task | โค้ด (ไฟล์: ฟังก์ชัน) | test (ผล) | สถานะ |
|---|---|---|---|---|---|
| FR-LNS-01 | AC-LNS-01 | T-03, T-04, T-05 | backend/app/api/loans.py: borrow_book; backend/app/services/loan_service.py: LoanService.borrow_book; frontend/src/pages/LoanKioskPage.jsx: handleSubmit | backend/tests/test_AC_LNS_01_loan_success_and_reminder.py: ผ่าน; frontend/src/__tests__/LoanKioskPage.test.jsx: ผ่าน | ครบ |
| FR-LNS-02 | AC-LNS-01, AC-LNS-02 | T-02, T-04, T-05 | backend/app/services/loan_service.py: LoanService.validate_loan; backend/app/repositories/loan_repository.py: member_active_loan_count, copy_is_borrowed | backend/tests/test_AC_LNS_01_loan_success_and_reminder.py, test_AC_LNS_02_loan_denied_when_limit_exceeded: ผ่าน; frontend/src/__tests__/LoanKioskPage.test.jsx: ผ่าน | ครบ |
| FR-LNS-03 | AC-LNS-01 | T-04, T-05 | backend/app/services/loan_service.py: LoanService.borrow_book; backend/app/services/notification_service.py: schedule_due_reminders; frontend/src/pages/LoanKioskPage.jsx: result alert | backend/tests/test_AC_LNS_01_loan_success_and_reminder.py: ผ่าน; frontend/src/__tests__/LoanKioskPage.test.jsx: ผ่าน | ครบ |
| FR-LNS-04 | AC-LNS-02 | T-02, T-04, T-05 | backend/app/services/loan_service.py: LoanService.validate_loan; backend/app/repositories/loan_repository.py: copy_is_borrowed; frontend/src/pages/LoanKioskPage.jsx: isDenied | backend/tests/test_AC_LNS_02_loan_denied_when_limit_exceeded.py: ผ่าน; frontend/src/__tests__/LoanKioskPage.test.jsx: ผ่าน | ครบ |
| FR-LNS-05 | AC-LNS-03 | T-06, T-07 | backend/app/api/loans.py: return_book; backend/app/services/loan_service.py: LoanService.return_book; frontend/src/pages/ReturnKioskPage.jsx: handleSubmit | backend/tests/test_AC_LNS_03_return_overdue_and_fine_shown.py: ผ่าน; frontend/src/__tests__/ReturnKioskPage.test.jsx: ผ่าน | ครบ |
| FR-LNS-06 | AC-LNS-03 | T-06, T-07 | backend/app/services/loan_service.py: LoanService.penalty_rate_for_copy, LoanService.return_book; backend/app/models/return_audit_log.py; frontend/src/pages/ReturnKioskPage.jsx: overdue and penalty display | backend/tests/test_AC_LNS_03_return_overdue_and_fine_shown.py: ผ่าน; frontend/src/__tests__/ReturnKioskPage.test.jsx: ผ่าน | ช่องโหว่ |
| FR-LNS-07 | AC-LNS-04 | T-08, T-09 | backend/app/api/loans.py: loan_history; backend/app/services/loan_service.py: LoanService.member_history; frontend/src/pages/LoanHistoryPage.jsx: loadHistory | backend/tests/test_AC_LNS_04_member_history_view.py: ผ่าน; frontend/src/__tests__/test_AC_LNS_04_member_history_view.test.jsx: ผ่าน | ครบ |
| CON-LNS-01 | AC-LNS-01, AC-LNS-02 | T-01, T-02, T-04 | backend/app/services/loan_service.py: LoanService.validate_loan; backend/app/repositories/loan_repository.py: member_active_loan_count, copy_is_borrowed | backend/tests/test_AC_LNS_01_loan_success_and_reminder.py, test_AC_LNS_02_loan_denied_when_limit_exceeded: ผ่าน | ครบ |
| CON-LNS-02 | AC-LNS-03 | T-01, T-06 | backend/app/services/loan_service.py: LoanService.return_book; backend/app/config.py: LOAN_DUE_DAYS, BOOK_GENERAL_PENALTY_PER_DAY_BAHT, BOOK_SPECIAL_PENALTY_PER_DAY_BAHT | backend/tests/test_AC_LNS_03_return_overdue_and_fine_shown.py: ผ่าน | ครบ |
| NFR-PRF-01 | ไม่มี AC | ไม่มี task ที่ชัดเจนในฟีเจอร์นี้ | ไม่มีที่ชัดเจนใน backend/app/ และ frontend/src/ สำหรับ 500 users pump ของ feature นี้ | ไม่มี test feature-specific; backend 전체มี test access 500 users แต่ไม่ใช่ borrow-return | ยังไม่ถึง |
| NFR-USB-01 | ไม่มี AC | T-05, T-07, T-09 | frontend/src/pages/LoanKioskPage.jsx, ReturnKioskPage.jsx, LoanHistoryPage.jsx; frontend/src/App.jsx | frontend/npm test: ผ่านทั้งหมด | ครบ |
| NFR-REL-01 | ไม่มี AC | ไม่มี task ที่ชัดเจนในฟีเจอร์นี้ | ไม่มี logic backup/replication หรือ audit/store redundancy ที่ชัดเจนใน feature นี้ | ไม่มี test feature-specific | ยังไม่ถึง |

## 2. ตามรอยย้อนกลับ (โค้ด ไป requirement)
| โค้ด (ไฟล์: ฟังก์ชัน หรือ endpoint) | อ้าง ID | ตรงกับข้อความใน spec ไหม | หมายเหตุ |
|---|---|---|---|
| POST /api/loans/borrow | FR-LNS-01, FR-LNS-02, FR-LNS-03, CON-LNS-01 | ใช่ | ตรวจ member, copy, limit, บันทึก loan, คืน due_date, และ schedule notification |
| POST /api/loans/return | FR-LNS-05, FR-LNS-06, CON-LNS-02 | ใช่ | ตรวจ active loan, คำนวณ overdue_days และ penalty_amount, บันทึก ReturnAuditLog |
| GET /api/loans/history/{member_id} | FR-LNS-07 | ใช่ | คืนประวัติยืม-คืนของ member ที่ร้องขอ พร้อมวันที่/สถานะ/ค่าปรับ |
| LoanService.validate_loan | FR-LNS-02, FR-LNS-04, CON-LNS-01 | ใช่ | ปฏิเสธเมื่อ invalid member, invalid copy, copy already borrowed, หรือ ยืมเกิน limit |
| LoanService.borrow_book | FR-LNS-01, FR-LNS-02, FR-LNS-03 | ใช่ | บันทึก LoanRecord, ตั้ง due_date, สร้าง notification schedule |
| LoanService.return_book | FR-LNS-05, FR-LNS-06, CON-LNS-02 | ใช่ | คำนวณค่าปรับและบันทึก audit log หลังคืนสำเร็จ |
| LoanHistoryPage / LoanKioskPage / ReturnKioskPage | FR-LNS-01 to FR-LNS-07 | ใช่ | UI ให้ยืม/คืน/ดูประวัติและแสดงผลตาม AC ส่วนใหญ่เหมาะสม |

## 3. ข้อค้นพบ
ชนิด: AC ไม่มี test / test อ่อน / โค้ดไม่มี FR / FR ไม่มี AC / เดา Q-xx / ละเมิด Constraint / ตัวเลขไม่ตรง spec / อ้าง ID ผิดเรื่อง
ทีมตัดสิน: แก้โค้ด / แก้ spec / เพิ่ม Q-xx / ไม่ใช่ปัญหา (พร้อมเหตุผล 1 บรรทัด)

| F-ID | ชนิด | อยู่ที่ | ขัดกับ | รายละเอียด | ทีมตัดสิน |
|---|---|---|---|---|---|
| F-LNS-001 | FR ไม่มี AC / อ้าง ID ผิดเรื่อง | spec.md: Out of scope, FR-LNS-06, ASM-03 | FR-LNS-06 และ Out of scope | Spec ระบุว่า “การคำนวณ/เรียกเก็บค่าปรับ” อยู่นอกขอบเขต แต่ FR-LNS-06 และ ASM-03 บังคับให้คำนวณและแสดงค่าปรับทันที จึงมีความขัดแย้งใน requirement เอง แม้โค้ดทำได้ตาม FR-LNS-06 | ว่าง |
| F-LNS-002 | AC ไม่มี test / test อ่อน | spec.md: NFR-PRF-01, NFR-REL-01 | ไม่พบ AC และไม่มี feature-specific test | NFR-PRF-01 และ NFR-REL-01 ระบุข้อกำหนดแต่ไม่มี Acceptance Criteria และไม่มี test ที่ตรวจเรื่องความพร้อมใช้งานพร้อมกัน 500 คน หรือการสำรองข้อมูลต่อ feature นี้ | ว่าง |
| F-LNS-003 | test อ่อน | backend/tests/test_AC_LNS_01_loan_success_and_reminder.py | AC-LNS-01 | Test ตรวจว่ามี payload ไม่ใช่การยืนยันว่าการแจ้งเตือนถูกส่งจริงในช่วง 1–3 วันก่อนกำหนดคืนเท่านั้น และไม่ได้ assert ว่า schedule ถูกสร้างในช่วงเวลาที่ถูกต้อง | ว่าง |

## 4. แก้แล้ว
| F-ID | แก้อย่างไร | รู้ได้อย่างไร |
|---|---|---|
| F-LNS-003 | ไม่ได้แก้โค้ดตามคำสั่ง /verify; จดไว้เฉพาะเป็นข้อค้นพบเพื่อทีมตรวจต่อ | เพราะ test เรียก API แล้ว assert ว่า payload มี notification แต่ไม่ได้ตรวจช่วงเวลา/จำนวนวันที่หรือว่า `due_date` ถูกต้องตามนโยบายจริง |
