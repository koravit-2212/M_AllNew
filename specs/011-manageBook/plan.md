# specs/011-manageBook/plan.md

1. สรุปแนวทาง
- ฟีเจอร์นี้ให้บรรณารักษ์/เจ้าหน้าที่จัดการข้อมูลหนังสือและบริการ (เพิ่ม/แก้ไข/ลบแบบ soft delete) โดยระบบต้องตรวจสอบรูปแบบข้อมูลก่อนบันทึกและบันทึก Audit Log เพื่อให้ข้อมูลที่แสดงต่อผู้ใช้เป็นปัจจุบัน
- ผู้ใช้: บรรณารักษ์ และเจ้าหน้าที่ห้องสมุด (ASM-01)
- แนวทาง: สร้าง UI แบบแอดมิน (React/Vite) + REST API (FastAPI) สำหรับ CRUD; ใช้ soft delete flag และเก็บ Audit Log แยก table; validate fields ตาม ASM-03

2. เทคโนโลยีที่ใช้
| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | UI แอดมินสำหรับจัดการ catalog |
| Backend: Python FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | REST API, JSON validation |
| Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | โครงสร้าง relational เหมาะกับ audit และ queries |
| Migrations: Alembic | ทีมเลือกเอง ไม่ได้มาจาก spec | จัดการ schema changes |
| Audit Log table | CON-AUDIT-01 | เก็บ actor, action, resource_id, timestamp, changes |
| TLS/HTTPS everywhere | CON-SEC-01 | ต้องเปิด HTTPS (reverse proxy / load balancer)

3. โมเดลข้อมูล (Entities)
- `catalog_items` (รองรับ FR-CAT-01, FR-CAT-02, FR-CAT-03, FR-CAT-04, AC-CAT-01/02/03)
  - id (PK)
  - title (string, required)  <-- ASM-03
  - resource_type (enum: book/service, required)  <-- ASM-03
  - call_number (string, required)  <-- ASM-03
  - isbn (string, nullable)  # validate ISBN-10/13 if present
  - metadata (jsonb, optional)
  - is_deleted (boolean, default false)  <-- ASM-02 (soft delete)
  - status (string) optional alternate to is_deleted
  - deleted_at (timestamp, nullable)  <-- ASM-02
  - deleted_by (user_id, nullable)  <-- ASM-02
  - created_by, created_at, updated_by, updated_at

- `audit_logs` (รองรับ CON-AUDIT-01, AC-CAT-02)
  - id (PK), actor_id, action (create/update/delete), resource_type, resource_id, timestamp, before, after, metadata

4. API / หน้าจอ
- Endpoints (รองรับ FRs):
  - `GET /admin/catalog` -> list items (query params: include_deleted=false)  (FR-CAT-01)
  - `GET /admin/catalog/{id}` -> get item details (FR-CAT-01)
  - `POST /admin/catalog` -> create item (body: title, resource_type, call_number, isbn, metadata) (FR-CAT-02, FR-CAT-03)
  - `PUT /admin/catalog/{id}` -> update item (body similar) (FR-CAT-02, FR-CAT-03)
  - `DELETE /admin/catalog/{id}` -> soft delete (sets is_deleted, deleted_at, deleted_by) (FR-CAT-02, ASM-02)
  - `GET /admin/catalog/{id}/audit` -> get audit history for item (CON-AUDIT-01)

- หน้าจอ (UI) (รองรับ FRs/ACs):
  - `Catalog List` — ตารางรายการ, ฟิลเตอร์, ปุ่ม Add/Edit/Delete (AC-CAT-01)
  - `Catalog Edit` — ฟอร์มสร้าง/แก้ไข พร้อม validation inline (AC-CAT-02, AC-CAT-03)
  - `Audit Log Viewer` — ดูประวัติการเปลี่ยนแปลงของรายการ (CON-AUDIT-01)

5. ตารางตรวจ Constraints
| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| CON-AUDIT-01 | `audit_logs` table, `GET /admin/catalog/{id}/audit`, บันทึกในทุก create/update/delete (FR-CAT-02, FR-CAT-03, AC-CAT-02) | ใช้แล้ว |
| CON-SEC-01 | ทุก endpoint ต้องให้บริการผ่าน HTTPS; คอนฟิก TLS ที่ reverse proxy / deployment (เทสบน staging ต้องเปิด HTTPS) | ใช้แล้ว |

6. แผนทดสอบจาก Acceptance Criteria
| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-CAT-01 | test_AC_CAT_01_show_item | เตรียมรายการใน DB แล้วเรียก `GET /admin/catalog/{id}` ยืนยัน response มีข้อมูลปัจจุบันและ UI แสดงข้อมูลครบ |
| AC-CAT-02 | test_AC_CAT_02_create_audit | เรียก `POST /admin/catalog` ด้วยข้อมูลถูกต้อง ยืนยัน status 201, ตรวจ DB ว่ามีรายการใหม่ และมี entry ใน `audit_logs` สำหรับ action=create |
| AC-CAT-03 | test_AC_CAT_03_validation_errors | เรียก `POST /admin/catalog` ด้วยข้อมูลที่ขาด `title` หรือ `call_number` ยืนยัน response 400 และไม่มีการบันทึกใน DB; UI แสดง error message ตาม field |

7. ลำดับงาน (5-10 ขั้น)
1. สร้าง database schema (catalog_items, audit_logs) และ migrations (FR-CAT-02, CON-AUDIT-01)
2. พัฒนา API endpoints พื้นฐาน (list/get/create/update/delete) พร้อม validation (FR-CAT-01, FR-CAT-02, FR-CAT-03)
3. พัฒนา Audit Log writing ที่ service layer (CON-AUDIT-01, AC-CAT-02)
4. สร้าง UI `Catalog List` และ `Catalog Edit` (React) พร้อม client-side validation (AC-CAT-01, AC-CAT-02)
5. เพิ่ม soft delete behavior และ hide from public queries (ASM-02)
6. เพิ่ม endpoint และ UI สำหรับดู Audit Log (CON-AUDIT-01)
7. เขียน integration tests และ E2E tests สำหรับ ACs (test_AC_CAT_01..03)
8. ทำ hardening ให้แน่ใจว่า TLS/HTTPS ถูกบังคับใช้งานใน deployment (CON-SEC-01)

8. สิ่งที่ยังไม่ทำ / Open Questions
- ขณะนี้ใน `spec.md` ไม่มี Open Questions ค้าง (Q-01/Q-02 ถูกตอบและบันทึกเป็น ASM-02/ASM-03). ส่วนที่เกี่ยวข้องกับคำถามใด ๆ จะยังไม่สร้างจนกว่าจะได้คำตอบเพิ่มเติมจากทีม

---

โปรดตรวจสอบ plan นี้ หากต้องการให้ผมเพิ่มตัวอย่าง regex สำหรับ ISBN หรือเปลี่ยนชื่อฟิลด์ (`is_deleted`/`deleted_at`/`deleted_by`) ให้แจ้งมา ผมจะอัปเดต `spec.md` และ `plan.md` ให้ตรงกัน
