# specs/012-announcements/plan.md

## 1. สรุปแนวทาง
- ฟีเจอร์นี้ให้เจ้าหน้าที่ประชาสัมพันธ์สร้างข่าวสาร/กิจกรรมแบบ draft, ตรวจสอบความถูกต้อง, และนำไปอนุมัติก่อนเผยแพร่สู่สาธารณะตามช่วงเวลาและสถานะการเผยแพร่ที่กำหนด
- ผู้ใช้หลัก: เจ้าหน้าที่ประชาสัมพันธ์, ผู้มีอำนาจ/ผู้ดูแลระบบ, และผู้ใช้บริการที่เข้ามาอ่านข่าวสารบนเว็บไซต์ห้องสมุด
- แนวทางการสร้าง: ใช้ React (Vite) สำหรับหน้าแอดมินและหน้า public, ใช้ Python FastAPI สำหรับบริการตรวจสอบและอนุมัติ, และมีการจัดเก็บข้อมูลข่าวสารพร้อมไฟล์แนบและการจัดตารางเวลาเผยแพร่แบบ Schedule Publish
- การตรวจสอบจะเริ่มจาก validation แบบอัตโนมัติ เช่น ฟิลด์บังคับ/ชนิดไฟล์/ขนาดไฟล์, แล้วต่อด้วย Approval Workflow ก่อนเผยแพร่จริงเพื่อให้กระบวนการสอดคล้องกับ FR-PRO-02 และ FR-PRO-04
- การเผยแพร่จะมี 2 รูปแบบ: Publish Now และ Schedule Publish โดยระบบต้องแสดงเฉพาะข่าวสารที่อยู่ในช่วงเวลาเผยแพร่ที่ถูกต้องบนหน้า public ตาม FR-PRO-03

## 2. เทคโนโลยีที่ใช้
| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | UI สำหรับเจ้าหน้าที่พิมพ์ข่าวสารและ UI public สำหรับอ่านข่าวสาร |
| Backend: Python FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | REST API สำหรับ create/update/validate/approve/publish |
| Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | เหมาะสำหรับเก็บข่าวสาร, ไฟล์แนบ, การอนุมัติ และเวลาเผยแพร่ |
| Scheduler: APScheduler หรือ cron job | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้จัดการ Schedule Publish และสลับสถานะเผยแพร่ตามเวลา |
| Storage สำหรับไฟล์แนบ | ทีมเลือกเอง ไม่ได้มาจาก spec | เก็บไฟล์ภาพ/เอกสารแบบแยกจาก metadata ของข่าวสาร |

## 3. โมเดลข้อมูล
- `announcements` (รองรับ FR-PRO-01, FR-PRO-02, FR-PRO-03)
  - id (PK)
  - title (string, required)  
  - content (text, required)
  - summary (text, nullable)
  - publish_mode (enum: publish_now, schedule)  
  - published_at (timestamp, nullable)  
  - starts_at (timestamp, nullable)
  - ends_at (timestamp, nullable)
  - approval_status (enum: draft, auto_validated, pending_approval, approved, rejected, published)
  - status (enum: active, inactive, archived)
  - created_by (user_id, required)
  - approved_by (user_id, nullable)
  - created_at, updated_at

- `announcement_attachments` (รองรับ FR-PRO-01, FR-PRO-04)
  - id (PK)
  - announcement_id (FK -> announcements.id)
  - file_name
  - mime_type
  - file_size
  - storage_path
  - uploaded_at

- `announcement_approvals` (รองรับ FR-PRO-02)
  - id (PK)
  - announcement_id (FK -> announcements.id)
  - approver_id
  - decision (approved/rejected)
  - reason (text, nullable)
  - approved_at

- `announcement_publish_jobs` (รองรับ FR-PRO-03)
  - id (PK)
  - announcement_id (FK -> announcements.id)
  - scheduled_for (timestamp)
  - action (publish/start/end)
  - is_active
  - last_run_at

> ข้อมูลที่เก็บในโมเดลนี้เป็นข้อมูลเกี่ยวกับข่าวสารและการอนุมัติเท่านั้น ไม่ได้เก็บข้อมูลนักศึกษา/บุคคลเฉพาะเจาะจงตาม spec; จึงไม่มีฟิลด์ที่ขัดกับข้อจำกัดด้านข้อมูลส่วนบุคคลที่ไม่ได้ระบุไว้

## 4. API / หน้าจอ
- `GET /admin/announcements` -> รายการข่าวสารในสถานะ draft, pending approval, approved, published (FR-PRO-01, FR-PRO-02)
- `POST /admin/announcements` -> สร้าง draft ข่าวสารพร้อมหัวข้อ/รายละเอียด/ไฟล์แนบ (FR-PRO-01)
- `GET /admin/announcements/{id}` -> ดูรายละเอียดข่าวสาร แบบมีประวัติการอนุมัติและไฟล์แนบ (FR-PRO-01, FR-PRO-02)
- `PUT /admin/announcements/{id}` -> แก้ไขหัวข้อ/รายละเอียด/สื่อประกอบที่ยังไม่เผยแพร่ (FR-PRO-01)
- `POST /admin/announcements/{id}/validate` -> ตรวจสอบอัตโนมัติว่าฟิลด์บังคับ ชนิดไฟล์ ขนาดไฟล์ ผ่านหรือไม่ (FR-PRO-02, FR-PRO-04)
- `POST /admin/announcements/{id}/approve` -> ส่งต่อให้ผู้มีอำนาจ/ผู้ดูแลระบบอนุมัติ (FR-PRO-02)
- `POST /admin/announcements/{id}/publish` -> เปิดเผยแพร่ทันที (Publish Now) หรือเข้าสู่ queue สำหรับ Schedule Publish (FR-PRO-03)
- `GET /public/announcements` -> รายการข่าวสารที่อยู่ในช่วงเวลาเผยแพร่และสถานะ active (FR-PRO-03)
- `GET /public/announcements/{id}` -> ดูรายละเอียดข่าวสารสาธารณะ (FR-PRO-03)

- หน้าจอ:
  - `Announcement List` — ดูรายการข่าวสาร, ตัวกรองสถานะอนุมัติ/เผยแพร่ (FR-PRO-01, FR-PRO-02, FR-PRO-03)
  - `Announcement Editor` — ฟอร์มกรอกหัวข้อ รายละเอียด และแนบไฟล์ (FR-PRO-01)
  - `Approval Panel` — ดูผล validation, เหตุผลปฏิเสธ และปุ่มอนุมัติ/ปฏิเสธ (FR-PRO-02, FR-PRO-04)
  - `Publish Scheduler` — ตั้งค่า Publish Now หรือระบุวัน-เวลาเริ่มและสิ้นสุดการเผยแพร่ (FR-PRO-03)
  - `Public Announcements Page` — แสดงข่าวสารที่เผยแพร่แล้วตามช่วงเวลา (FR-PRO-03)

## 5. ตารางตรวจ Constraints
| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| ไม่มี Constraint/DOM/IF ใน spec.md | spec.md ของ feature นี้ระบุว่า “ไม่มี Business Rule เฉพาะ” และไม่มี Constraint ที่บังคับเพิ่มเติม | ใช้แล้ว (ไม่มีข้อบังคับเพิ่มเติมที่ต้องจัดการ) |

## 6. แผนทดสอบจาก Acceptance Criteria
| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-PRO-01 | test_AC_PRO_01_publish_announcement_success | สร้างข่าวสารด้วยข้อมูลครบถ้วน, ผ่าน validation แบบอัตโนมัติ, ผ่าน Approval Workflow, แล้วเรียก publish-now หรือ schedule-publish; ยืนยันว่า public page แสดงข้อมูลตามช่วงเวลาและสถานะที่กำหนด |
| AC-PRO-02 | test_AC_PRO_02_reject_invalid_announcement | ส่งข้อมูลที่ขาดฟิลด์บังคับหรือไฟล์แนบผิดรูปแบบ/เกินขนาด; ยืนยัน response ปฏิเสธการเผยแพร่และมีข้อความแจ้งเหตุผล; ตรวจว่าข้อมูลไม่ปรากฏบน public page |

## 7. ลำดับงาน
1. สร้าง schema สำหรับ `announcements`, `announcement_attachments`, `announcement_approvals`, `announcement_publish_jobs` พร้อม validation baseline (FR-PRO-01, FR-PRO-02)
2. พัฒนา API create/update และ upload file สำหรับเจ้าหน้าที่ประชาสัมพันธ์ (FR-PRO-01)
3. พัฒนา validation แบบอัตโนมัติสำหรับข้อมูลบังคับ/ชนิดไฟล์/ขนาดไฟล์ และ error response (FR-PRO-02, FR-PRO-04)
4. สร้าง Approval Workflow สำหรับผู้มีอำนาจหรือผู้ดูแลระบบ พร้อมบันทึกผลการอนุมัติ (FR-PRO-02)
5. สร้างโหมด Publish Now และ Schedule Publish พร้อมการคำนวณช่วงเวลาเริ่ม/สิ้นสุดที่แสดงบน public page (FR-PRO-03)
6. พัฒนา public listing/detail page ให้แสดงเฉพาะข่าวสารที่ active และอยู่ในช่วงเวลาเผยแพร่ที่ถูกต้อง (FR-PRO-03)
7. ทดสอบ end-to-end สำหรับ AC-PRO-01 และ AC-PRO-02 และตรวจสอบ responsiveness บนคอมพิวเตอร์/มือถือ (FR-PRO-01, FR-PRO-02, FR-PRO-03, NFR-USB-01)
8. ทำ QA final และตรวจสภาพแวดล้อมการ deploy สำหรับ schedule runner และ file upload ที่ใช้จริง (FR-PRO-03, NFR-USB-01)

## 8. สิ่งที่ยังไม่ทำ
- ขณะนี้ใน spec.md ไม่มี Open Questions ที่ค้างหลังจากขั้น clarify; ถ้ามีคำตอบใหม่จากทีมภายหลัง จะต้องกลับมาอัปเดตแผนนี้โดยตรงตาม item ที่เกี่ยวข้อง
- ส่วนที่เกี่ยวข้องกับคำถามหรือข้อสรุปที่ยังไม่ได้มีใน spec จะยังไม่สร้างจนกว่าจะได้รับคำตอบจากทีม

---
