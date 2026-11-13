# Feature: ยืม-คืนหนังสือ (Book Loan / Return)
Spec ID: SPEC-LNS-001 | อ้างอิง: plan.md | วันที่: 13 พฤศจิกายน 2569

## สรุป
- มี 4 เฟสหลักและ 9 task รวมทั้งหมด โดยเริ่มจากฐานรากก่อนแล้วค่อยทำเส้นหลัก 3 เส้น: ยืม, คืน/ค่าปรับ, และประวัติผู้ใช้
- มี 0 task ที่รอ Q-xx เพราะ spec และ plan ได้กำหนดคำตัดสินชัดเจนสำหรับการแจ้งเตือนล่วงหน้าและอัตราค่าปรับแล้ว
- เฟสแรกที่ลองใช้งานได้จริงคือ เฟส 1: "ยืมหนังสือสำเร็จและปฏิเสธเมื่อเกินโควตา" ซึ่งครอบคลุม AC-LNS-01 และ AC-LNS-02

## เฟส 0: ฐานราก (schema / seed / service shell)

### T-01 สร้าง schema การยืม-คืนและสถานะหนังสือ
- รองรับ: FR-LNS-01, FR-LNS-02, FR-LNS-05, CON-LNS-01, CON-LNS-02
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-01
- ไฟล์ที่แตะ: `backend/app/models/book_copy.py`, `backend/app/models/loan_record.py`, `backend/app/models/notification_log.py`, `backend/app/models/return_audit_log.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: schema ของ `BookCopy` และ `LoanRecord` พร้อมฟิลด์ `status`, `due_date`, `return_time`, `overdue_days`, `penalty_amount` และ `notification_log`/audit log สามารถบันทึกได้
- สถานะ: เสร็จ รอทีมตรวจ

#### จุดตรวจเฟส 0
- test ที่ต้องผ่านทั้งหมด: `test_T01_loan_schema`, `test_T02_loan_validation`, `test_T03_loan_seed_data`
- เปิดระบบ: `cd /workspaces/M_AllNew/backend && uvicorn app.main:app --reload` และ `cd /workspaces/M_AllNew/frontend && npm run dev`
- คนลองเองตามฐานราก:
  - Given ระบบยังไม่ได้มีข้อมูลยืมคืนใด ๆ และมีตัวอย่างหนังสือ 1 เล่มพร้อมสถานะพร้อมให้ยืม
  - When เริ่มทำงานหรือโหลด seed data
  - Then ระบบต้องสร้างข้อมูลเริ่มต้นที่จำเป็นสำหรับยืม/คืน/ประวัติได้โดยไม่ล้ม
- ยังขาด: ไม่มี

### T-02 สร้าง service ตรวจสิทธิ์ยืมและสถานะหนังสือ
- รองรับ: FR-LNS-02, FR-LNS-04, CON-LNS-01
- ตรวจด้วย: AC-LNS-02
- ไฟล์ที่แตะ: `backend/app/services/loan_service.py`, `backend/app/repositories/loan_repository.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: service ตรวจพบกรณียืมครบโควตาและหนังสือถูกยืมอยู่แล้วได้อย่างชัดเจน พร้อมคืนค่าเหตุผลที่หน้าจอและ API ใช้ต่อได้
- สถานะ: เสร็จ รอทีมตรวจ

### T-03 ตั้ง seed data และ route shell สำหรับ API ยืม-คืน
- รองรับ: FR-LNS-01, FR-LNS-05, FR-LNS-07
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-03
- ไฟล์ที่แตะ: `backend/app/api/loans.py`, `backend/app/main.py`, `backend/app/services/member_profile_seed.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01, T-02
- เสร็จเมื่อ: API route `POST /api/loans/borrow`, `POST /api/loans/return`, `GET /api/loans/history/{member_id}` สามารถเรียกได้ และข้อมูล seed รองรับการทดสอบการยืม-คืนได้
- สถานะ: เสร็จ รอทีมตรวจ

## เฟส 1: ยืมหนังสือสำเร็จและปฏิเสธเมื่อเกินโควตา (AC-LNS-01, AC-LNS-02)

### T-04 สร้าง API ยืมหนังสือและจัดตารางแจ้งเตือนล่วงหน้า
- รองรับ: FR-LNS-01, FR-LNS-02, FR-LNS-03, FR-LNS-04, CON-LNS-01
- ตรวจด้วย: AC-LNS-01, AC-LNS-02
- ไฟล์ที่แตะ: `backend/app/api/loans.py`, `backend/app/services/loan_service.py`, `backend/app/repositories/loan_repository.py`, `backend/app/services/notification_service.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01, T-02, T-03
- เสร็จเมื่อ: `POST /api/loans/borrow` บันทึก `LoanRecord` ได้, คืน `due_date` ที่ถูกต้อง, ตั้ง `NotificationLog` ให้ส่งล่วงหน้า 1–3 วัน, และปฏิเสธเมื่อหนังสือถูกยืมอยู่หรือยืมครบโควตา
- สถานะ: เสร็จ รอทีมตรวจ

### T-05 สร้างหน้าเครื่องยืมหนังสือพร้อมผลสำเร็จ/ปฏิเสธ
- รองรับ: FR-LNS-01, FR-LNS-02, FR-LNS-03, FR-LNS-04
- ตรวจด้วย: AC-LNS-01, AC-LNS-02
- ไฟล์ที่แตะ: `frontend/src/pages/LoanKioskPage.jsx`, `frontend/src/api/client.js`, `frontend/src/App.jsx`
- แบบหน้าจอ: `UI-LNS-01-borrow.html`
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: หน้าเครื่องยืมแสดงสถานะ "ยืมสำเร็จ" กับวันกำหนดคืนและข้อความแจ้งเตือนล่วงหน้า, และแสดง "ไม่สามารถยืมได้" เมื่อครบโควตาหรือหนังสือถูกยืมอยู่แล้ว
- สถานะ: เสร็จ รอทีมตรวจ

#### จุดตรวจเฟส 1
- test ที่ต้องผ่านทั้งหมด: `test_AC_LNS_01_loan_success_and_reminder`, `test_AC_LNS_02_loan_denied_when_limit_exceeded`, และ test ของเฟส 0
- เปิดระบบ: `cd /workspaces/M_AllNew/backend && uvicorn app.main:app --reload` และ `cd /workspaces/M_AllNew/frontend && npm run dev`
- คนลองเองตาม AC-LNS-01:
  - Given นักศึกษามีสิทธิ์ยืมและหนังสือเล่มที่ต้องการยังว่างอยู่
  - When นักศึกษาสแกนบัตรและสแกนหนังสือบนหน้าเครื่องยืม
  - Then ระบบต้องบันทึกการยืม, แสดงวันกำหนดคืน, และแจ้งว่าจะแจ้งเตือนล่วงหน้า 1–3 วันก่อนกำหนดคืน
- คนลองเองตาม AC-LNS-02:
  - Given นักศึกษาได้ยืมถึงจำนวนสูงสุดแล้วหรือหนังสือถูกยืมอยู่
  - When พยายามยืมเพิ่มอีก
  - Then ระบบต้องไม่อนุญาตและแสดงเหตุผลที่ชัดเจน
- ยังขาด: ไม่มี

## เฟส 2: คืนหนังสือและแสดงค่าปรับเมื่อเกินกำหนด (AC-LNS-03)

### T-06 สร้าง API คืนหนังสือและคำนวณค่าปรับแบบเกินกำหนด
- รองรับ: FR-LNS-05, FR-LNS-06, CON-LNS-02
- ตรวจด้วย: AC-LNS-03
- ไฟล์ที่แตะ: `backend/app/api/loans.py`, `backend/app/services/loan_service.py`, `backend/app/models/return_audit_log.py`, `backend/app/repositories/loan_repository.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: `POST /api/loans/return` บันทึกการคืน, คำนวณ `overdue_days` และ `penalty_amount` อย่างถูกต้องตามอัตรา 3 บาท/วัน (หนังสือทั่วไป) และ 20 บาท/วัน (หนังสือสำรอง/โสตทัศนวัสดุ/อุปกรณ์), และบันทึก `ReturnAuditLog` ให้เจ้าหน้าที่ตรวจสอบได้
- สถานะ: เสร็จ รอทีมตรวจ

### T-07 สร้างหน้าคืนหนังสือและแสดงค่าปรับทันที
- รองรับ: FR-LNS-05, FR-LNS-06
- ตรวจด้วย: AC-LNS-03
- ไฟล์ที่แตะ: `frontend/src/pages/ReturnKioskPage.jsx`, `frontend/src/api/client.js`, `frontend/src/App.jsx`
- แบบหน้าจอ: `UI-LNS-02-return-history.html`
- ต้องทำหลัง: T-06
- เสร็จเมื่อ: หน้าคืนหนังสือแสดงข้อความ "คืนสำเร็จ" พร้อมจำนวนวันที่เกินกำหนดและยอดค่าปรับทันทีหลังบันทึกการคืนสำเร็จ
- สถานะ: เสร็จ รอทีมตรวจ

#### จุดตรวจเฟส 2
- test ที่ต้องผ่านทั้งหมด: `test_AC_LNS_03_return_overdue_and_fine_shown`, และ test ของเฟส 0-1
- เปิดระบบ: `cd /workspaces/M_AllNew/backend && uvicorn app.main:app --reload` และ `cd /workspaces/M_AllNew/frontend && npm run dev`
- คนลองเองตาม AC-LNS-03:
  - Given นักศึกษานำหนังสือที่เกินกำหนดคืนกลับมาคืน
  - When นักศึกษาสแกนหนังสือคืนบนหน้าคืนหนังสือ
  - Then ระบบต้องบันทึกการคืน, แจ้งจำนวนวันที่เกินกำหนด, และแสดงยอดค่าปรับทันที พร้อมบันทึกลง audit log
- ยังขาด: ไม่มี

## เฟส 3: ตรวจประวัติการยืม-คืนของผู้ใช้ (AC-LNS-04)

### T-08 สร้าง API ดูประวัติการยืม-คืนของสมาชิก
- รองรับ: FR-LNS-07
- ตรวจด้วย: AC-LNS-04
- ไฟล์ที่แตะ: `backend/app/api/loans.py`, `backend/app/services/loan_service.py`, `backend/app/repositories/loan_repository.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-06
- เสร็จเมื่อ: `GET /api/loans/history/{member_id}` ส่งคืนรายการยืมคืนที่มีวันที่ยืม, วันครบกำหนด, วันที่คืนจริง, สถานะ, และค่าปรับหากมี
- สถานะ: เสร็จ รอทีมตรวจ

### T-09 สร้างหน้าประวัติการยืม-คืนของผู้ใช้
- รองรับ: FR-LNS-07
- ตรวจด้วย: AC-LNS-04
- ไฟล์ที่แตะ: `frontend/src/pages/LoanHistoryPage.jsx`, `frontend/src/api/client.js`, `frontend/src/App.jsx`
- แบบหน้าจอ: `UI-LNS-02-return-history.html`
- ต้องทำหลัง: T-08
- เสร็จเมื่อ: หน้าแสดงประวัติยืม-คืนของผู้ใช้ครบถ้วนตาม mockup และแสดงสถานะต่าง ๆ อย่างถูกต้อง เช่น คืนแล้ว / ยังไม่คืน / ค่าปรับ
- สถานะ: เสร็จ รอทีมตรวจ

#### จุดตรวจเฟส 3
- test ที่ต้องผ่านทั้งหมด: `test_AC_LNS_04_member_history_view`, และ test ของเฟส 0-2
- เปิดระบบ: `cd /workspaces/M_AllNew/backend && uvicorn app.main:app --reload` และ `cd /workspaces/M_AllNew/frontend && npm run dev`
- คนลองเองตาม AC-LNS-04:
  - Given นักศึกษาเคยมีประวัติการยืม-คืนหนังสืออย่างน้อย 2 รายการ
  - When เปิดดูประวัติการยืม-คืนของตนเอง
  - Then ระบบต้องแสดงประวัติที่ถูกต้องครบถ้วนตามวันที่และสถานะ
- ยังขาด: ไม่มี

## ตารางตรวจความครบ

### 1) AC ID | task ที่ตรวจ AC นี้
| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-LNS-01 | T-04, T-05 |
| AC-LNS-02 | T-02, T-04, T-05 |
| AC-LNS-03 | T-06, T-07 |
| AC-LNS-04 | T-08, T-09 |

### 2) Constraint ID | task ที่ทำให้เป็นจริง
| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| CON-LNS-01 | T-01, T-02, T-04 |
| CON-LNS-02 | T-01, T-06 |

### 3) FR ID | AC ที่ตรวจ FR นี้ | เฟส
| FR ID | AC ที่ตรวจ FR นี้ | เฟส |
|---|---|---|
| FR-LNS-01 | AC-LNS-01 | เฟส 1 |
| FR-LNS-02 | AC-LNS-01 | เฟส 1 |
| FR-LNS-03 | AC-LNS-01 | เฟส 1 |
| FR-LNS-04 | AC-LNS-02 | เฟส 1 |
| FR-LNS-05 | AC-LNS-03 | เฟส 2 |
| FR-LNS-06 | AC-LNS-03 | เฟส 2 |
| FR-LNS-07 | AC-LNS-04 | เฟส 3 |

## สิ่งที่ยังไม่ทำ
- ไม่มี Open Questions ใน spec.md ของฟีเจอร์นี้ ณ ปัจจุบัน
- task ที่เกี่ยวข้องกับการแจ้งเตือนล่วงหน้าและอัตราค่าปรับไม่ใช่ "รอ Q-xx" เนื่องจากมีคำตอบชัดเจนใน ASM-02 และ ASM-03 และถูกนำไปใช้ใน T-04/T-06 แล้ว
