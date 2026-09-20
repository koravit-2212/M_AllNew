# แผนงาน: จัดการข้อมูลผู้ใช้บริการ (User Management)

## 1. สรุปแนวทาง (5 บรรทัด)
- ฟีเจอร์นี้ให้เจ้าหน้าที่สามารถค้นหา ตรวจสอบ และแก้ไขข้อมูลผู้ใช้บริการ รวมถึงประวัติการเข้าใช้บริการและการยืม-คืน โดยมีการควบคุมสิทธิ์ตามบทบาทที่ชัดเจน
- ผู้ใช้หลักคือ เจ้าหน้าที่ทั่วไปที่ให้บริการประจำวัน และผู้ดูแลระบบ/IT ที่รับผิดชอบการจัดการข้อมูลระดับสูงและตรวจสอบ Audit Log
- ระบบจะมีหน้า Dashboard สำหรับค้นหาผู้ใช้และหน้า Detail สำหรับดูประวัติการเข้าใช้และการยืม-คืน พร้อมฟังก์ชันแก้ไขข้อมูลที่ต้องผ่านสิทธิ์และบันทึก Audit Log
- การออกแบบจะเน้นความปลอดภัยของข้อมูลส่วนบุคคลและการควบคุมสิทธิ์ก่อนเข้าถึงเมนู/ฟังก์ชันทุกระดับ ตาม DOM-PRV-01 และ FR-USM-01
- แผนนี้สร้างจาก spec.md ใน Draft v2 และทุกส่วนจะชี้กลับไปหา ID ของ spec เพื่อให้ traceability ครอบคลุมทุก FR, NFR, CON และ AC ที่เกี่ยวข้อง

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| React + Vite สำหรับหน้าเว็บจัดการข้อมูลผู้ใช้บริการ | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ dashboard, search form, detail view และ action form สำหรับแก้ไขข้อมูล |
| Python FastAPI สำหรับ API จัดการค้นหา/ดู/แก้ไขข้อมูลผู้ใช้และ Audit Log | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ service layer และ validation ตามสิทธิ์และ policy |
| PostgreSQL สำหรับเก็บข้อมูลผู้ใช้, ประวัติการเข้าใช้บริการ, ประวัติการยืม-คืน, และ Audit Log | ทีมเลือกเอง ไม่ได้มาจาก spec | รองรับการบันทึกที่ต้องมีความถูกต้องและเป็นปัจจุบัน |
| HTTPS สำหรับการสื่อสารทุกจุด | CON-SEC-01 | บังคับใช้ทุก endpoint และ channel ที่ใช้ข้อมูลผู้ใช้ |
| Audit Log repository สำหรับบันทึกผู้เข้าถึง เวลา และรายการที่เปลี่ยนแปลง | CON-AUDIT-01 | ต้องบันทึกสำหรับการดูและแก้ไขแบบมีสิทธิ์ทุกครั้ง |

## 3. โมเดลข้อมูล

| Entity | ฟิลด์หลัก | รองรับ FR |
|---|---|---|
| UserProfile | user_id, student_id, full_name, email, phone, status, role, last_updated_at | FR-USM-01, FR-USM-02, FR-USM-03 |
| PermissionPolicy | role_name, can_view, can_edit, can_add, can_delete, effective_from, approved_by | FR-USM-01, FR-USM-04 |
| ServiceAccessHistory | access_log_id, user_id, accessed_at, accessed_by, action_type, source_channel | FR-USM-02 |
| BorrowReturnHistory | history_id, user_id, item_id, item_type, checkout_at, due_at, returned_at, status | FR-USM-02 |
| AuditLog | log_id, actor_user_id, actor_role, action_type, target_user_id, changed_fields, performed_at, source_ip, approval_note | FR-USM-03, FR-USM-04 |

หมายเหตุ:
- ไม่เก็บข้อมูลเลขประจำตัวประชาชนหรือฟิลด์บัตรประชาชนที่ไม่ได้ระบุไว้ใน spec ตาม DOM-PRV-01 เพื่อให้เรารักษาขอบเขตข้อมูลส่วนบุคคลตามนโยบายมหาวิทยาลัยและกฎหมายที่เกี่ยวข้อง
- PermissionPolicy ควรเป็นศูนย์กลางสิทธิ์เพื่อให้ FR-USM-01 และ FR-USM-04 ทดสอบได้ด้วยการยืนยันบทบาทก่อนเข้าถึงเมนูและฟังก์ชันต่าง ๆ

## 4. API / หน้าจอ

- Web page: User Management Dashboard — แสดงฟอร์มค้นหาโดยรหัสนักศึกษาหรือชื่อ และปุ่มเข้าดูรายละเอียดผู้ใช้
  - รองรับ: FR-USM-01, FR-USM-02
- GET /api/users/search?query={studentIdOrName} — input: keyword / output: list ของ UserProfile ที่ตรงเงื่อนไข
  - รองรับ: FR-USM-02
- GET /api/users/{userId}/details — output: profile, service access history, borrow/return history
  - รองรับ: FR-USM-02
- PATCH /api/users/{userId} — input: changedFields และ actor metadata / output: updated profile + audit record id
  - รองรับ: FR-USM-01, FR-USM-03
- POST /api/users/{userId}/audit-log — input: actor, action, reason, changedFields / output: log created
  - รองรับ: FR-USM-03, FR-USM-04
- GET /api/audit-logs?userId={userId}&role={actorRole} — output: entries ที่มีสิทธิ์ดูได้ตามบทบาท
  - รองรับ: FR-USM-03, FR-USM-04
- Web page: Access Denied Banner — แสดงข้อความปฏิเสธการเข้าถึงเมื่อเจ้าหน้าที่ไม่มีสิทธิ์
  - รองรับ: FR-USM-04

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| DOM-PRV-01 | การกำหนด entity UserProfile, AuditLog และการป้องกันข้อมูลส่วนบุคคลอย่าเก็บฟิลด์ที่ไม่ได้ระบุใน spec; จำกัดการเข้าถึงตามบทบาท | ใช้แล้ว |
| CON-SEC-01 | ทุกหน้าและ API ใช้ HTTPS; สร้าง deployment policy ที่บังคับ TLS สำหรับ frontend/backend | ใช้แล้ว |
| CON-AUDIT-01 | AuditLog model และ API บันทึกผู้เข้าถึง เวลา และรายการที่เปลี่ยนแปลง พร้อมใช้ในทุกการดู/แก้ไขข้อมูล | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-USM-01 | test_AC_USM_01_update_profile_with_audit | จำลองเจ้าหน้าที่ที่มีสิทธิ์แก้ไขข้อมูลผู้ใช้, แก้ไขค่าหนึ่งค่า, ตรวจว่า DB อัปเดตและมี Audit Log เก็บข้อมูลผู้ทำ เวลา และ field ที่เปลี่ยน |
| AC-USM-02 | test_AC_USM_02_access_denied_for_unauthorized_user | จำลองเจ้าหน้าที่ที่ไม่มีสิทธิ์เข้าถึงเมนู, ลองเข้าหน้าการจัดการข้อมูลหรือเรียก PATCH API, ตรวจว่าระบบปฏิเสธและแสดงข้อความแจ้งเตือน |
| AC-USM-03 | test_AC_USM_03_search_user_and_view_history | จำลองค้นหาด้วยรหัสนักศึกษาและชื่อ, ตรวจว่า API คืนข้อมูลผู้ใช้พร้อมประวัติการเข้าใช้บริการและการยืม-คืนที่ถูกต้อง |
| AC-USM-04 | test_AC_USM_04_audit_log_for_personal_data_access | จำลองการเปิดดูและแก้ไขข้อมูลส่วนบุคคล, ตรวจว่ามี audit log ที่ระบุผู้เข้าถึง เวลา และรายการที่เปลี่ยนแปลง |

## 7. ลำดับงาน

1. กำหนด role matrix และ PermissionPolicy สำหรับเจ้าหน้าที่ทั่วไป, System Admin/IT, และ PDPA viewer (FR-USM-01, FR-USM-04)
2. สร้างหน้า Dashboard สำหรับค้นหาโดยรหัสนักศึกษาหรือชื่อและเชื่อมกับ API search (FR-USM-02)
3. สร้างหน้า Detail ฉบับผู้ใช้ที่รวมข้อมูลผู้ใช้, ประวัติการเข้าใช้บริการ, และประวัติการยืม-คืน (FR-USM-02)
4. สร้าง flow แก้ไขข้อมูลผู้ใช้และ validation ผ่านสิทธิ์ก่อนบันทึก (FR-USM-01, FR-USM-03)
5. สร้าง AuditLog service สำหรับบันทึกผู้ทำการ เปลี่ยนแปลง เวลา และ field ที่แก้ไข (CON-AUDIT-01, FR-USM-03)
6. สร้าง Access Denied flow แบบ user-friendly สำหรับผู้ไม่มีสิทธิ์ และบันทึกเหตุการณ์ปฏิเสธ (FR-USM-04)
7. ทดสอบ end-to-end สำหรับ AC-USM-01 ถึง AC-USM-04 โดยรวม security, privacy, และ audit trail (AC-USM-01 - AC-USM-04)
8. ตรวจสอบนโยบายการเก็บข้อมูลสิทธิ์และ retention ต่อ requirement ความปลอดภัยและ PDPA ตาม DOM-PRV-01 และ ASM-03 (NFR-SEC-01, NFR-SEC-02)

## 8. สิ่งที่ยังไม่ทำ

- ไม่มี Open Questions ใน spec ปัจจุบันหลังจากการ clarify แล้ว จึงไม่มีข้อที่ต้องรอคำตอบก่อนสร้างฟังก์ชันนี้
- ส่วนที่เกี่ยวข้องกับการกำหนดรายละเอียดสิทธิ์แบบย่อยต่อบทบาทจะยังไม่ถูกสร้างจนกว่าจะมีคำตอบจากฝ่าย IT หรือผู้บริหารห้องสมุดเพื่อยืนยันตารางสิทธิ์ที่ละเอียดขึ้น

---

## หมายเหตุการใช้งาน
- แผนนี้ใช้ spec.md ใน Draft v2 เป็นแหล่งความจริง
- การเลือกเทคโนโลยี (React + Vite, FastAPI, PostgreSQL) เป็นทางเลือกของทีม ไม่ได้มาจาก spec แต่ไม่ขัดกับ Constraints ที่มีอยู่
