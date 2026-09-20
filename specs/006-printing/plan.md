# plan.md for specs/006-printing/spec.md

## 1. สรุปแนวทาง
ฟีเจอร์นี้ให้นักศึกษาส่งงานพิมพ์จากไฟล์ที่รองรับ กำหนดจำนวนหน้า/จำนวนชุด และยืนยันการพิมพ์เพื่อให้ระบบส่งงานไปยัง print spooler ของฝ่าย IT และบันทึกประวัติการใช้บริการ
ผู้ใช้เป้าหมาย: นักศึกษา (ผ่าน SU-IT Account)
แนวทางการสร้าง: หน้าเว็บ (React + Vite) ให้ผู้ใช้เลือก/อัปโหลดไฟล์ แสดงตัวเลือกการพิมพ์และค่าใช้จ่ายฝั่งไคลเอ็นต์/เซิร์ฟเวอร์ แล้วเรียก API หลังบ้าน (FastAPI) เพื่อส่งงานไปยัง print spooler และบันทึกธุรกรรม
ข้อจำกัดสำคัญ: ต้องเชื่อมต่อกับ print spooler ที่ฝ่าย IT กำหนด และต้อง validate ชนิด/ขนาดไฟล์ตาม spec

## 2. เทคโนโลยีที่ใช้
สิ่งที่เลือก | มาจาก | หมายเหตุ
---|---|---
Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | UI responsive บนคอมพิวเตอร์และมือถือ (อิง NFR-USB-01)
Backend: Python + FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | เลือกเพื่องาน API และการ integrate กับ print spooler
Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | เก็บ metadata ของงานพิมพ์และประวัติการหักโควตา
Print integration: Print Spooler API / Connector (ตาม IF-PRN-01) | IF-PRN-01 | ต้องรับค่า endpoint/credentials จากฝ่าย IT
File storage: Object storage (local disk / S3) | ทีมเลือกเอง ไม่ได้มาจาก spec | เก็บไฟล์ชั่วคราวก่อนส่งไป spooler
Authentication: SU-IT SSO integration (OAuth/SAML) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับยืนยันผู้ใช้และดึงโควตา

## 3. โมเดลข้อมูล (Entity หลัก)
- `PrintJob` (รองรับ FR-PRT-03, FR-PRT-02)
  - id (PK)
  - user_id (อ้างถึง SU-IT account)
  - file_id (FK -> PrintFile)
  - pages_requested (int)
  - copies (int)
  - color_mode ("BW"|"Color")
  - total_cost (decimal)
  - status ("ready"|"queued"|"sent"|"failed"|"cancelled")
  - created_at, updated_at
- `PrintFile` (รองรับ FR-PRT-01, FR-PRT-04)
  - id (PK)
  - filename
  - content_type
  - size_bytes
  - pages_detected (nullable)
  - stored_path
  - uploaded_at
- `UserQuota` (รองรับ ASM-03, FR-PRT-02)
  - user_id (PK)
  - term_id
  - free_credit_remaining (decimal)
  - bw_pages_used (int)
  - color_pages_used (int)
- `PrintTransaction` (รองรับ FR-PRT-03, traceability)
  - id
  - printjob_id
  - debit_amount
  - source ("SU-IT-Quota"|"manual")
  - timestamp
  - note
- `PrinterStatus` (รองรับ FR-PRT-05, IF-PRN-01)
  - printer_id
  - status (ready|offline|error)
  - last_checked_at

หมายเหตุ: spec ห้ามเก็บข้อมูลส่วนที่ถูกจำกัดโดย Constraint ใดๆ ไม่มีข้อห้ามเฉพาะเจาะจงใน spec ดังนั้นตารางข้างต้นไม่เก็บข้อมูลส่วนบุคคลเพิ่มเติมนอกเหนือจากที่จำเป็น (user_id อ้าง SU-IT)

## 4. API / หน้าจอ
Endpoints (หลัก) — แต่ละรายการระบุ FR ที่รองรับ
- POST /api/print/upload
  - Input: multipart file, color_mode, copies
  - Output: { file_id, pages_detected }
  - รองรับ: FR-PRT-01, FR-PRT-04
- GET /api/print/options?file_id={id}
  - Input: file_id
  - Output: {pages, estimated_cost, allowed_color_modes}
  - รองรับ: FR-PRT-02, AC-PRT-01
- POST /api/print/submit
  - Input: file_id, pages, copies, color_mode, target_printer_id (optional)
  - Output: { printjob_id, status }
  - Behavior: ตรวจสอบโควตา (UserQuota), บันทึก PrintJob, ส่งไปยัง print spooler (IF-PRN-01)
  - รองรับ: FR-PRT-03, FR-PRT-02
- GET /api/print/jobs/{id}
  - Input: job id
  - Output: job status, history
  - รองรับ: FR-PRT-03
- GET /api/printers/status
  - Input: -
  - Output: list of printers + status
  - รองรับ: FR-PRT-05, IF-PRN-01

หน้าจอ (UI)
- Upload & Preview (รองรับ FR-PRT-01)
- Print Options & Cost Preview (รองรับ FR-PRT-02, AC-PRT-01)
- Confirm & Submit (รองรับ FR-PRT-03, AC-PRT-02)
- Job Status / History (รองรับ FR-PRT-03)

## 5. ตารางตรวจ Constraints
Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ
---|---|---
IF-PRN-01 | Integration: /api/print/submit จะเรียก Print Spooler API; มีตัวแปร config สำหรับ endpoint/credentials | ใช้แล้ว
CON-FILE-01 | Validation ที่ /api/print/upload และ frontend จะปฏิเสธไฟล์ที่ไม่ใช่ PDF/DOCX/PPTX/XLSX/JPG/PNG หรือขนาด > 50MB | ใช้แล้ว

## 6. แผนทดสอบจาก Acceptance Criteria
AC ID | ชื่อ test | ทดสอบอย่างไร
---|---|---
AC-PRT-01 | test_AC_PRT_01_CostPreview | อัปโหลดไฟล์ที่รองรับ, ระบุจำนวนหน้าและชุด, ตรวจสอบว่าค่าใช้บริการที่แสดงตรงกับสูตรการคำนวณ (ใช้ UserQuota สมมติ)
AC-PRT-02 | test_AC_PRT_02_PrintFlow | ตั้งค่าสถานะ printer เป็น ready (mock spooler), ยืนยันการพิมพ์ -> ตรวจสอบว่ามีการเรียก spooler และผู้ใช้ได้รับเอกสารตามจำนวน (integration test แบบ end-to-end หรือ mock)
AC-PRT-03 | test_AC_PRT_03_PrinterNotReady | ตั้งค่าสถานะ printer เป็น offline/error -> พยายามยืนยันการพิมพ์ -> ตรวจสอบว่าระบบแจ้งเตือนและไม่ส่งงานพิมพ์
AC-PRT-04 | test_AC_PRT_04_UnsupportedFile | อัปโหลดไฟล์ประเภทไม่รองรับหรือใหญ่เกินขนาด -> ตรวจสอบว่าระบบแจ้งเตือนและไม่อนุญาตให้ดำเนินการต่อ

หมายเหตุการทดสอบ: การทดสอบที่เกี่ยวกับ print spooler ต้องใช้ mock/stub ของ spooler API ในสภาพแวดล้อมทดสอบ หรือทำกับ test spooler ที่ฝ่าย IT จัดเตรียม

## 7. ลำดับงาน (5–10 ขั้น)
1. ตั้งค่าโปรเจกต์ frontend/back-end และ authentication integration (รองรับ NFR-USB-01) — FR-PRT-01, NFR-USB-01
2. พัฒนา endpoint `/api/print/upload` พร้อม validation ตาม CON-FILE-01 และการเก็บไฟล์ชั่วคราว — FR-PRT-01, FR-PRT-04
3. พัฒนาการตรวจจับจำนวนหน้าและคำนวณค่าใช้บริการ (`/api/print/options`) รวมการอ่านโควตาผู้ใช้จาก `UserQuota` — FR-PRT-02, AC-PRT-01
4. พัฒนา `/api/print/submit` เพื่อสร้าง PrintJob, บันทึก PrintTransaction และเรียก Print Spooler API (mock support) — FR-PRT-03, AC-PRT-02
5. พัฒนา endpoint สำหรับตรวจสอบสถานะเครื่องพิมพ์และ job status (`/api/printers/status`, `/api/print/jobs/{id}`) — FR-PRT-05
6. เขียน integration tests และ E2E tests ที่ mock spooler และทดสอบ AC ทั้ง 4 — AC-PRT-01..04
7. ทำงาน UX และ responsive tweaks บน frontend, รวมข้อความแจ้งเตือนกรณีข้อผิดพลาด — NFR-USB-01, FR-PRT-04, FR-PRT-05
8. เตรียม deployment/config สำหรับการเชื่อมต่อ spooler จริงกับฝ่าย IT และเอกสารการตั้งค่า credentials — IF-PRN-01

## 8. สิ่งที่ยังไม่ทำ / Open Questions
- ปัจจุบันใน `spec.md` ไม่มี Open Questions ค้างอยู่ (Q-01 และ Q-02 ถูกตอบและย้ายเป็น ASM-02 / ASM-03 / ASM-04)

> ส่วนที่เกี่ยวข้องกับคำถามที่ยังไม่มีคำตอบจะยังไม่ถูกสร้างจนกว่าจะได้คำตอบจากฝ่ายที่เกี่ยวข้อง (ในที่นี้ไม่มีข้อ Open Questions ค้าง)

---

บันทึก: แผนนี้อ้างอิงกับ ID ใน spec (`FR-PRT-01` ... `AC-PRT-04`, `IF-PRN-01`, `CON-FILE-01`, `ASM-02`..`ASM-04`).
