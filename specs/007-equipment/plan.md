### 1. สรุปแนวทาง
ฟีเจอร์นี้ให้บริการยืมอุปกรณ์ของห้องสมุด (เช่น ปลั๊กไฟ, ร่ม, ถุงผ้า และอุปกรณ์ไอที/โสตทัศนวัสดุ) แก่นักศึกษา โดยนักศึกษาสามารถเลือกอุปกรณ
'tและส่งคำขอยืมให้เจ้าหน้าที่ตรวจสอบและอนุมัติ ทีมจะออกแบบเป็นเว็บแอปที่มีหน้ารายการอุปกรณ์ หน้าส่งคำขอ และหน้าจอเจ้าหน้าที่สำหรับตรวจสอบ/อนุมัติ/override โดยระบบบันทึกสต็อกและบันทึกการยืมพร้อม due date ตามประเภทอุปกรณ์

### 2. เทคโนโลยีที่ใช้
สิ่งที่เลือก | มาจาก | หมายเหตุ
---|---|---
Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ UI responsive บนคอมพิวเตอร์และมือถือ (สอดคล้อง NFR-USB-01)
Backend: Python (FastAPI) | ทีมเลือกเอง ไม่ได้มาจาก spec | REST API, เหมาะกับการออกแบบ CRUD และ background tasks
Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | เก็บข้อมูล inventory และ loan records
Auth: University SSO / JWT | CON-LNS-02 (เชื่อมกับระบบสมาชิกมหาวิทยาลัย) | ถ้าต้องผสาน SSO ให้ทีม IT เป็นผู้กำหนดรายละเอียด
Hosting: Docker / K8s (optional) | ทีมเลือกเอง ไม่ได้มาจาก spec | สำหรับ deployment

### 3. โมเดลข้อมูล (Entities หลัก)
- `equipment_type` (รองรับ FR-EQP-01, FR-EQP-04, AC-EQP-01)
	- id, name, category (e.g., convenience, it_audio), default_loan_days, max_quantity_per_loan (nullable)
- `equipment_item` (รองรับ FR-EQP-02, FR-EQP-05)
	- id, equipment_type_id, identifier, status (available/loaned/maintenance)
- `student` (รองรับ FR-EQP-03)
	- student_id, name, status, outstanding_returns_count, outstanding_fines_amount
- `loan_record` (รองรับ FR-EQP-04, FR-EQP-06, AC-EQP-02)
	- id, student_id, equipment_type_id, quantity, loan_date, due_date, status (pending/approved/declined/returned), approved_by, override_by, notes
- `audit_log` (รองรับการบันทึก Override และการอนุมัติ)
	- id, actor_id, action, target_id, timestamp, reason

หมายเหตุ: ไม่มีฟิลด์ข้อมูลที่ขัดกับ Constraints ใน spec (เช่น หมายเลขบัตรประชาชน ไม่ได้ระบุไว้ จึงไม่เก็บ)

### 4. API / หน้าจอ (สั้น)
- GET /api/equipment-types -> รายการประเภทอุปกรณ์ (FR-EQP-01, AC-EQP-01)
	- output: list of equipment_type with available count
- POST /api/loan-requests -> สร้างคำขอยืม (FR-EQP-02, FR-EQP-03)
	- input: student_id, equipment_type_id, quantity
	- output: request id, status=pending หรือ error(insufficient)
- GET /api/loan-requests/{id} -> ดูสถานะคำขอ (FR-EQP-02)
- POST /api/loan-requests/{id}/approve -> เจ้าหน้าที่อนุมัติ (FR-EQP-03, FR-EQP-04)
	- input: approver_id, action(approve/decline), optional: override=true
	- side-effect: สร้าง loan_record, ปรับ stock, set due_date ตาม equipment_type.default_loan_days
- POST /api/loan-requests/{id}/override -> เจ้าหน้าที่ที่มีสิทธิ์ปลดล็อก (ASM-02)
- POST /api/loan-requests/{id}/return -> ทำรายการคืน (update loan_record status, adjust stock)

หน้าจอ:
- Student: Equipment list, Request form (รองรับ AC-EQP-01)
- Staff: Pending requests list, Request detail + Approve/Decline/Override (รองรับ FR-EQP-03/04/06)
- Admin: Inventory view (อ่านค่า, ไม่ครอบคลุมการจัดการประเภทตาม spec Out of scope)

### 5. ตารางตรวจ Constraints
Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ
---|---|---
CON-LNS-02 | Validation ก่อนอนุมัติใน `POST /api/loan-requests` และ UI เจ้าหน้าที่ (block ผู้มี outstanding) | ใช้แล้ว

### 6. แผนทดสอบจาก Acceptance Criteria
AC ID | ชื่อ test | ทดสอบอย่างไร
---|---|---
AC-EQP-01 | test_AC-EQP-01_show_equipment_types | เปิดหน้าจอยืมอุปกรณ์โดยนักศึกษาที่ล็อกอิน ตรวจสอบว่ารายการประเภทแสดงตาม `equipment_type` ที่มีใน DB
AC-EQP-02 | test_AC-EQP-02_approve_and_record | สร้างคำขอที่มีจำนวนเพียงพอและนักศึกษาไม่มีรายการค้างคืน ให้เจ้าหน้าที่อนุมัติ -> ยืนยันว่า `loan_record` ถูกสร้างและ `equipment_item` count ลดลง
AC-EQP-03 | test_AC-EQP-03_out_of_stock_message | ทำให้ equipment_type.cnt=0 แล้วนักศึกษาขอยืม -> ยืนยันว่า API/UI แจ้งว่าไม่สามารถยืมได้
AC-EQP-04 | test_AC-EQP-04_block_when_outstanding | ทำให้นักศึกษามี outstanding_returns หรือ outstanding_fines แล้วส่งคำขอ -> ยืนยันว่าระบบบล็อกคำขอ และเฉพาะเจ้าหน้าที่ที่มีสิทธิ์เท่านั้นที่สามารถ Override ได้

### 7. ลำดับงาน (งานย่อย 7 ขั้น)
1) สร้างโครงร่าง DB และ entity `equipment_type`, `equipment_item`, `loan_record` (FR-EQP-01, FR-EQP-02, FR-EQP-04)
2) สร้าง API อ่านรายการประเภทอุปกรณ์ และหน้า UI แสดงรายการ (AC-EQP-01)
3) สร้าง API สำหรับสร้างคำขอยืม และ logic ตรวจ stock / outstanding (FR-EQP-02, FR-EQP-03, AC-EQP-03)
4) สร้างหน้าจอเจ้าหน้าที่สำหรับดูคำขอและอนุมัติ/ปฏิเสธ (FR-EQP-03, AC-EQP-02)
5) เพิ่มฟีเจอร์การบันทึก due_date ตาม `equipment_type.default_loan_days` และการลด stock เมื่ออนุมัติ (FR-EQP-04)
6) เพิ่มฟังก์ชัน Override สำหรับเจ้าหน้าที่ รวม Audit Log (ASM-02)
7) เขียนชุด unit/integration tests ตามตาราง AC และทดสอบ concurrency case (Q8 ยังไม่ได้ตอบ แต่ทดสอบแบบ first-come-first-served เป็นค่าเริ่มต้น)

### 8. สิ่งที่ยังไม่ทำ (Open Questions)
- ขณะนี้ใน `spec.md` ไม่มี Open Questions ค้างอยู่ (Q-01 และ Q-02 ถูกตอบและถูกย้ายเป็น ASM-02/ASM-03)

---

บันทึก: แผนนี้อ้างอิงตรงกับ ID ใน `specs/007-equipment/spec.md` สำหรับทุกบรรทัดที่เกี่ยวข้องกับ FR/AC/CON/ASM
