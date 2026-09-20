# specs/005-borrow-return/plan.md

## 1. สรุปแนวทาง (5 บรรทัด)
- ฟีเจอร์นี้ให้ผู้ใช้บริการ (นักศึกษา/บุคลากร) ยืมหนังสือผ่านเครื่องอัตโนมัติหรือเคาน์เตอร์ และคืนหนังสือด้วยการสแกนบาร์โค้ด/QR Code เพื่อให้ระบบควบคุมสิทธิ์และสถานะหนังสือได้ถูกต้อง
- แนวทางสร้างคือแยกกระบวนการเป็น 3 ส่วนหลัก: ตรวจสิทธิ์/ยืม, ตรวจสอบการคืนและคำนวณเลยกำหนด, และติดตามประวัติ/การแจ้งเตือนของผู้ใช้
- ระบบจะบันทึกข้อมูลยืมคืนและวันกำหนดส่งคืนไว้ในรายการยืมต่อผู้ใช้ พร้อมส่งการแจ้งเตือนล่วงหน้า 1–3 วันผ่านระบบแจ้งเตือนและอีเมล
- เมื่อคืนเกินกำหนด ระบบจะแสดงจำนวนวันที่เกินกำหนดและยอดค่าปรับทันทีหลังบันทึกการคืนสำเร็จ พร้อมบันทึกเหตุการณ์เพื่อให้เจ้าหน้าที่ตรวจสอบได้
- หน้าที่หลักของแอปพลิเคชันคือให้ผู้ใช้ยืม/คืนได้, แจ้งผลอย่างชัดเจน, และให้ดูประวัติยืม-คืนของตนเองได้ตาม FR-LNS-01 ถึง FR-LNS-07

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับหน้า Web บนคอมพิวเตอร์และมือถือ ตาม NFR-USB-01 |
| Backend: Python (FastAPI) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ API ยืมคืน, ตรวจสิทธิ์, ประวัติ และการแจ้งเตือน |
| Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้เก็บข้อมูลสมาชิก, การยืม, การคืน, ประวัติ และ log การแจ้งเตือน |
| Notification Service: ระบบแจ้งเตือนในตัว + SMTP/Email | ทีมเลือกเอง ไม่ได้มาจาก spec | รองรับการแจ้งเตือนล่วงหน้า 1–3 วัน ตาม ASM-02 |
| Audit Log: table / event log | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้เก็บข้อมูลการคืนเกินกำหนดและผลค่าปรับเพื่อดูย้อนหลัง |

## 3. โมเดลข้อมูล

| Entity | ฟิลด์หลัก | รองรับ FR |
|---|---|---|
| Member | member_id, member_type, full_name, card_id, email, status | FR-LNS-01, FR-LNS-02, FR-LNS-07 |
| BookCopy | copy_id, barcode, title, status, availability, last_loan_record_id | FR-LNS-01, FR-LNS-04, FR-LNS-05 |
| LoanRecord | loan_id, member_id, copy_id, borrow_time, due_date, return_time, status, overdue_days, penalty_amount | FR-LNS-02, FR-LNS-03, FR-LNS-05, FR-LNS-06 |
| NotificationLog | notification_id, member_id, loan_id, type, scheduled_at, sent_at, channel, status | FR-LNS-03 |
| ReturnAuditLog | audit_id, loan_id, member_id, overdue_days, penalty_amount, processed_at, actor | FR-LNS-06 |

หมายเหตุ:
- ข้อมูลที่จำเป็นสำหรับประวัติการยืม-คืนจะเก็บใน `LoanRecord` และ `ReturnAuditLog` เพื่อให้ผู้ใช้ดูประวัติของตัวเองได้ (FR-LNS-07)
- ระบบไม่จำเป็นต้องเก็บข้อมูลค่าปรับแบบแยกตามนโยบายการเรียกเก็บเงินอย่างสมบูรณ์ เพราะตาม spec ระบุว่า “คำนวณ/เรียกเก็บค่าปรับ” ยังอยู่นอกขอบเขตของฟีเจอร์นี้ (Out of scope) แต่ค่าปรับที่คำนวณได้เพื่อแสดงผลหลังคืนเกินกำหนดจะจัดเก็บเป็นข้อมูลใน `LoanRecord` และ `ReturnAuditLog` เท่านั้น

## 4. API / หน้าจอ

- POST /api/loans/borrow
  - input: member_id, barcode, source (automated_machine|counter)
  - output: loan_id, due_date, status, message
  - รองรับ: FR-LNS-01, FR-LNS-02, FR-LNS-03, AC-LNS-01
- POST /api/loans/return
  - input: member_id, barcode
  - output: loan_id, return_status, overdue_days, penalty_amount, message
  - รองรับ: FR-LNS-05, FR-LNS-06, AC-LNS-03
- GET /api/loans/history/{member_id}
  - input: member_id
  - output: list of loan history items with borrow date, due date, return date, status
  - รองรับ: FR-LNS-07, AC-LNS-04
- POST /api/notifications/schedule
  - input: loan_id, due_date, member_id
  - output: notification_status, channels
  - รองรับ: FR-LNS-03, ASM-02
- GET /api/loans/{loan_id}/audit
  - input: loan_id
  - output: overdue_days, penalty_amount, processed_at, actor
  - รองรับ: FR-LNS-06

หน้าจอ
- หน้าเครื่องยืม/คืน (automated machine / counter)
  - ใส่บัตรและสแกนหนังสือ, แสดงผลอนุญาต/ปฏิเสธและวันกำหนดคืน
  - รองรับ: FR-LNS-01, FR-LNS-02, FR-LNS-03, FR-LNS-04
- หน้าประวัติการยืม-คืนของผู้ใช้
  - แสดงรายการยืมคืน, สถานะ, วันที่ครบกำหนด, วันที่คืนจริง, และข้อมูลเกินกำหนด
  - รองรับ: FR-LNS-07, AC-LNS-04

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| CON-LNS-01 | ใช้ในกระบวนการยืมที่ต้องตรวจสอบสิทธิ์ก่อนบันทึก `LoanRecord` และปฏิเสธกรณีไม่ผ่านเงื่อนไขใน `POST /api/loans/borrow` | ใช้แล้ว |
| CON-LNS-02 | ใช้ในกระบวนการคืนและคำนวณ `overdue_days`, `penalty_amount` ใน `POST /api/loans/return` และในกรอบเวลาการแจ้งเตือน/การประเมินเกินกำหนด | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-LNS-01 | test_AC_LNS_01_loan_success_and_reminder | จำลองนักศึกษามีสิทธิ์ยืมและหนังสือพร้อมใช้; รัน `POST /api/loans/borrow` แล้วตรวจสอบว่าระบบบันทึก `LoanRecord` ได้, คืน `due_date` ถูกต้อง, และสร้าง `NotificationLog` อย่างน้อยหนึ่งรายการผ่านระบบแจ้งเตือน/อีเมล |
| AC-LNS-02 | test_AC_LNS_02_loan_denied_when_limit_exceeded | จำลองกรณีสมาชิกยืมถึงโควตาหรือหนังสือถูกยืมอยู่แล้ว; รัน `POST /api/loans/borrow` แล้วตรวจสอบ response มีสถานะปฏิเสธและ message ระบุเหตุผลชัดเจน |
| AC-LNS-03 | test_AC_LNS_03_return_overdue_and_fine_shown | จำลองหนังสือเกินกำหนดคืน; รัน `POST /api/loans/return` แล้วตรวจสอบว่า `overdue_days` และ `penalty_amount` ถูกคำนวณตามอัตรา, ระบบแสดงผลทันที, และบันทึก `ReturnAuditLog` |
| AC-LNS-04 | test_AC_LNS_04_member_history_view | จำลองประวัติการยืมคืนหลายรายการ; รัน `GET /api/loans/history/{member_id}` แล้วตรวจสอบว่ารายการแสดงครบถ้วนและถูกต้องตามโซนวันที่/สถานะ |

## 7. ลำดับงาน

1. กำหนด schema และฟิลด์ของ `Member`, `BookCopy`, `LoanRecord`, `NotificationLog`, `ReturnAuditLog` ตาม FR-LNS-01 ถึง FR-LNS-07
2. สร้าง API ยืมหนังสือ `POST /api/loans/borrow` พร้อมตรวจสิทธิ์และปฏิเสธเมื่อผิดเงื่อนไข (FR-LNS-01, FR-LNS-02, FR-LNS-04)
3. สร้าง API คืนหนังสือ `POST /api/loans/return` พร้อมคำนวณ `overdue_days` และ `penalty_amount` และบันทึก Audit Log (FR-LNS-05, FR-LNS-06)
4. สร้างระบบแจ้งเตือนล่วงหน้า 1–3 วัน และเชื่อมกับช่องทางแจ้งเตือน + อีเมล (FR-LNS-03, ASM-02)
5. สร้าง API ดูประวัติการยืมคืน `GET /api/loans/history/{member_id}` และ UI หน้าแสดงประวัติ (FR-LNS-07, AC-LNS-04)
6. สร้างหน้าเครื่องยืม/คืนสำหรับเคาน์เตอร์หรืออัตโนมัติ รวมถึงข้อความแจ้งผลให้ชัดเจน (FR-LNS-01, FR-LNS-04, AC-LNS-01, AC-LNS-02)
7. ทดสอบตาม AC-LNS-01 ถึง AC-LNS-04 และปรับข้อความ/logic ตามผลทดสอบ (AC-LNS-01, AC-LNS-02, AC-LNS-03, AC-LNS-04)

## 8. สิ่งที่ยังไม่ทำ
- ขณะนี้ใน `spec.md` ไม่มี Open Questions ที่ค้างอยู่ เพราะคำถามเดิมเกี่ยวกับการแจ้งเตือนล่วงหน้าและค่าปรับได้ถูกตัดสินเป็น `ASM-02` และ `ASM-03` แล้ว
- ดังนั้นส่วนที่เกี่ยวข้องกับการแจ้งเตือน 1–3 วัน และค่าปรับ 3 บาท/วัน / 20 บาท/วัน จะยังไม่เปลี่ยนแปลงจนกว่าทีมจะมีคำตัดสินใจใหม่

---

สรุปสั้น ๆ ตามข้อที่ต้องรายงาน:
1) Constraint ที่ยังไม่ได้ใช้: ไม่มี — ทั้ง `CON-LNS-01` และ `CON-LNS-02` ถูกนำไปใช้ในกระบวนการยืม/คืนแล้ว
2) AC ที่ทดสอบยากหรือทดสอบไม่ได้: `AC-LNS-03` เป็น test ที่ต้องจำลองวันที่เกินกำหนดและค่าปรับจริง, รวมถึงการบันทึกเหตุการณ์ลงระบบ; หากไม่มีข้อมูลยืมคืนแบบตัวอย่างจริง อาจไม่ทดสอบได้เต็มที่
3) สิ่งที่อยากเดาแต่ไม่ได้เดา: ยังไม่มีการระบุว่าแต่ละประเภทสมาชิก (นักศึกษา/บุคลากร) มีจำนวนหนังสือสูงสุดหรืออัตราค่าปรับที่แตกต่างกันหรือไม่, จึงยังคงเป็นเรื่องที่ต้องเป็น `ASM-01`/`ASM-03` ตามนโยบายจริงของห้องสมุด
