# plan.md for specs/013-manageSystem

## 1. สรุปแนวทาง
- ฟีเจอร์นี้เป็นเมนูกลาง (Dashboard/Navigation Center) สำหรับเจ้าหน้าที่ห้องสมุดที่มีสิทธิ์ เพื่อเลือกและไปยังหน้าจอจัดการข้อมูลเฉพาะ (หนังสือ/บริการ/ข้อมูลการใช้บริการ) ที่อยู่ใน UC-10/UC-11
- UC-13 จะไม่ทำการจัดการข้อมูล CRUD โดยตรง แต่ต้องตรวจสอบสิทธิ์และแสดงรายการประเภทข้อมูล รวมถึงให้สามารถเรียกดูข้อมูลการใช้บริการ (read-only) เพื่อการตรวจสอบย้อนหลัง
- การเข้าถึงทุกหน้าและฟังก์ชันย่อยจะควบคุมด้วย RBAC ตามที่ทีมสรุป (ASM-04)
- ระบบต้องบันทึก Audit Log สำหรับการกระทำสำคัญที่เกิดจาก Dashboard (CON-AUDIT-01) และต้องปฏิบัติตามนโยบายความเป็นส่วนตัว (DOM-PRV-01) และใช้งานผ่านการเชื่อมต่อที่ปลอดภัย (CON-SEC-01)
- แนวทางการพัฒนา: frontend เป็น SPA (Dashboard) ที่เรียก backend API สำหรับการตรวจสอบสิทธิ์ การดึงรายการประเภทข้อมูล และการดู Usage Records (read-only); การจัดการ CRUD ที่แท้จริงจะเป็นการนำทาง/เชื่อมต่อไปยังบริการของ UC-10/UC-11

## 2. เทคโนโลยีที่ใช้
สิ่งที่เลือก | มาจาก | หมายเหตุ
---|---|---
Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ตามข้อแนะนำของรายวิชา
Backend: Python (FastAPI) | ทีมเลือกเอง ไม่ได้มาจาก spec | เบา, รวดเร็วสำหรับ API
Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | เก็บ `usage_records` และ `audit_log`
Auth: OAuth2 / JWT (library) | ทีมเลือกเอง ไม่ได้มาจาก spec | ต้องรองรับ RBAC และใช้ HTTPS (CON-SEC-01)

## 3. โมเดลข้อมูล (สรุปเฉพาะฟิลด์หลัก)
Entity (ตาราง) — ฟิลด์หลัก — รองรับ FR

- `usage_records` — `id`, `entity_type` (book/service), `entity_id`, `action` (borrow/return/access), `performed_by`, `performed_at`, `metadata` (json) — รองรับ FR-SYS-02 (แสดงข้อมูลการใช้บริการ), FR-SYS-04 (ตรวจสอบ/บันทึก)
- `audit_log` — `id`, `user_id`, `action`, `resource_type`, `resource_id`, `timestamp`, `ip`, `before` (json|null), `after` (json|null) — รองรับ CON-AUDIT-01, FR-SYS-04, AC-SYS-01
- `rbac_roles` (reference) — `role_id`, `role_name`, `permissions` (json) — รองรับ FR-SYS-01, FR-SYS-05
- `dashboard_links` — (ไม่จำเป็นต้องเก็บถาวร แต่ถ้าต้องการเก็บ) `id`, `type` (book/service/usage), `target_url`, `label` — รองรับ FR-SYS-02

โน้ต: ข้อมูลเช่นรายละเอียดหนังสือ/ผู้ใช้/บริการ จะอ้างอิงจากระบบ UC-10/UC-11 และไม่เก็บซ้ำในฐานข้อมูลของ UC-13 เพื่อหลีกเลี่ยงความซ้ำซ้อนของ Business Logic (ตาม ASM-03/ASM-04)

## 4. API / หน้าจอ (สรุป)
- GET /admin/dashboard
  - description: ดึงข้อมูลสรุปและรายการประเภทข้อมูลที่ผู้ใช้เข้าถึงได้
  - input: JWT token, query params (optional)
  - output: list of data types, quick-stats
  - รองรับ: FR-SYS-01, FR-SYS-02, AC-SYS-04

- GET /admin/usage-records
  - description: ดึงรายการ `usage_records` (read-only, filterable)
  - input: JWT token, filters (date range, entity_type, entity_id, paging)
  - output: list of usage records, paging
  - รองรับ: FR-SYS-02, ASM-02

- POST /admin/authorize
  - description: ตรวจสอบสิทธิ์การเข้าถึงเมนู/ฟังก์ชัน (RBAC check)
  - input: JWT token, resource
  - output: allowed: true/false, permissions
  - รองรับ: FR-SYS-01, FR-SYS-05

- POST /admin/redirect-to-management
  - description: เมื่อผู้ใช้เลือกประเภทข้อมูลและรายการ ให้ backend คืน URL หรือ token เพื่อนำทางไปยังหน้าที่เกี่ยวข้องของ UC-10/UC-11 (delegation)
  - input: type, entity_id
  - output: target_url / action_token
  - รองรับ: FR-SYS-03 (โดย delegation), FR-SYS-02

- (Frontend) หน้า `Dashboard` — แสดงประเภทข้อมูล, ปุ่มนำทางไป UC-10/UC-11 — รองรับ FR-SYS-02, AC-SYS-04
- (Frontend) หน้า `Usage Records` — ตารางค้นหา/กรองแบบ read-only — รองรับ FR-SYS-02, ASM-02

## 5. ตารางตรวจ Constraints
Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ
---|---|---
DOM-PRV-01 | เกี่ยวกับการออกแบบ `usage_records` และ `audit_log`: ไม่เก็บข้อมูลส่วนบุคคลเกินที่จำเป็น, เข้ารหัส/จำกัดการเข้าถึง | ใช้วิธี: ใช้เฉพาะฟิลด์ที่จำเป็น, เข้ารหัสช่องข้อมูลที่เป็น PII, มอบสิทธิ์การเข้าถึงตาม RBAC — ใช้แล้ว
CON-AUDIT-01 | `audit_log` table และเรียกบันทึกทุก action สำคัญจาก Dashboard (เช่น redirect, authorize, view sensitive) | ใช้แล้ว
CON-SEC-01 | ทุก endpoint ต้องบังคับใช้ HTTPS, auth (OAuth2/JWT), และตรวจสอบ input | ใช้แล้ว

## 6. แผนทดสอบจาก Acceptance Criteria
AC ID | ชื่อ test | ทดสอบอย่างไร
---|---|---
AC-SYS-01 | test_AC_SYS_01_save_and_audit | Given: เจ้าหน้าที่ที่มีสิทธิ์ (create test user with role) เมื่อกดดำเนินการจากหน้าที่นำทาง (redirect) ให้ตรวจสอบว่ามีการสร้าง audit_log entry และ API ตอบ success (ถ้า operation ถูก delegate ให้ตรวจสอบว่า redirect/action_token ถูกสร้างและบันทึก)
AC-SYS-02 | test_AC_SYS_02_validation_failure | Given: ส่ง payload ที่ไม่ถูกต้องไปยัง service ที่ delegate เมื่อกดยืนยัน ระบบต้องแสดงข้อผิดพลาดและไม่มีบันทึกใน DB (เช็กว่าไม่มี `before/after` ใน audit สำหรับการบันทึกที่ล้มเหลว)
AC-SYS-03 | test_AC_SYS_03_unauthorized_access | Given: ผู้ใช้ไม่มีสิทธิ์ เมื่อพยายามเข้าเมนู Dashboard หรือเรียก API ต้องได้รับการปฏิเสธ (HTTP 403) และแสดงข้อความแจ้งเตือน
AC-SYS-04 | test_AC_SYS_04_show_data_types | Given: เจ้าหน้าที่ที่มีสิทธิ์ เมื่อเปิด `GET /admin/dashboard` ระบบต้องแสดงรายการประเภทข้อมูลทั้ง 3 (หนังสือ, บริการ, ข้อมูลการใช้บริการ)

## 7. ลำดับงาน (งานย่อย 7 ขั้น)
1. ตั้งค่าโปรเจกต์ skeleton — frontend (React/Vite) + backend (FastAPI) + DB migrations (รองรับ FR-SYS-01) — รองรับ: FR-SYS-01, AC-SYS-04
2. สมัคร/ออกแบบโมเดล `rbac_roles` และระบบตรวจสอบสิทธิ์ (Auth) — ทดสอบ FR-SYS-01, FR-SYS-05
3. พัฒนา endpoint `GET /admin/dashboard` และ UI Dashboard (แสดงประเภทข้อมูลและสถิติ) — รองรับ FR-SYS-02, AC-SYS-04
4. พัฒนา `usage_records` read-only API และหน้าแสดง (filter, paging) — รองรับ ASM-02, FR-SYS-02
5. พัฒนา `audit_log` writer ใน backend และเชื่อมการบันทึกกับ actions ของ Dashboard (redirect, authorize, view sensitive) — รองรับ CON-AUDIT-01, AC-SYS-01
6. ทำ integration กับ UC-10/UC-11 สำหรับ delegation (redirect/action_token) — รองรับ FR-SYS-03
7. เขียน automated tests ตาม AC ทั้งหมด, ทดสอบ security/PRIVACY checks, จัดทำเอกสารและสรุปการส่งมอบ

## 8. สิ่งที่ยังไม่ทำ (Open Questions)
- ณ ตอนนี้ใน `spec.md` ไม่มี Open Questions ค้าง (Q-01/Q-02 ได้รับคำตอบและบันทึกเป็น ASM-02 ถึง ASM-04) — ดังนั้นไม่มีส่วนที่ถูกบล็อกจาก Open Questions

---

(ไฟล์นี้ร่างโดยอิงจาก `specs/013-manageSystem/spec.md` — ทุกบรรทัดในแผนสามารถ trace กลับไปหา FR/CON/AC ที่เกี่ยวข้องได้)
