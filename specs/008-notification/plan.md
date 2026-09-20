# Plan for Feature: รับข่าวสารและการแจ้งเตือน (Notifications)
สรุปแนวทาง: ฟีเจอร์นี้อนุญาตให้เจ้าหน้าที่สร้างข่าวสาร/ประกาศแล้วระบบบันทึกและส่งแจ้งเตือนไปยังนักศึกษาที่เกี่ยวข้องผ่านช่องทาง LINE, Email, และ In‑App. ผู้ใช้หลักคือเจ้าหน้าที่ห้องสมุด (สร้าง/เลือกกลุ่ม) และนักศึกษารับการแจ้งเตือน. แนวทางคือเก็บข่าวสารในฐานข้อมูล, ใช้งานคิวแบบ asynchronous สำหรับการส่ง, และบันทึกการพยายามส่งเพื่อ retry/audit.

## 1. สรุปแนวทาง (5 บรรทัด)
- ฟีเจอร์: สร้าง/จัดการข่าวสารและส่งแจ้งเตือนไปยังนักศึกษา
- ผู้ใช้: เจ้าหน้าที่ห้องสมุด (ผู้สร้าง/กำหนดกลุ่ม), นักศึกษา (ผู้รับ)
- แนวทางเทคนิค: บันทึก Notification ใน DB, enqueue งานส่งไปยัง worker ที่ติดต่อกับช่องทางภายนอก
- ความน่าเชื่อถือ: retry policy (สูงสุด 3 ครั้ง, exponential backoff) และ fallback channel
- UI: หน้า Create Notification พร้อม Dynamic Filters, Saved Segments และ CSV upload

## 2. เทคโนโลยีที่ใช้
สิ่งที่เลือก | มาจาก | หมายเหตุ
---|---|---
Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับหน้าเจ้าหน้าที่และจัดการ segments
Backend: Python FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | REST API + worker integration
Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | persistent storage สำหรับ notifications, attempts, segments
Queue: Redis + RQ / Celery | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ enqueue งานส่งแบบ asynchronous
Storage for attachments: Object Storage (S3 compatible) | ทีมเลือกเอง ไม่ได้มาจาก spec | ถ้รองรับไฟล์ต่อไปในอนาคต

## 3. โมเดลข้อมูล (Entities)
- Notification
  - id (PK)
  - title
  - body
  - author_id (เจ้าหน้าที่)
  - created_at, publish_at, expires_at
  - target_segment_id (nullable)
  - channels (array: [LINE,EMAIL,IN_APP])
  - supports: FR-NTF-01, FR-NTF-02, FR-NTF-03

- NotificationDeliveryAttempt
  - id (PK)
  - notification_id (FK)
  - student_id
  - channel
  - attempt_count
  - last_error (text)
  - status (pending/sent/failed)
  - next_retry_at
  - supports: FR-NTF-04

- SavedSegment
  - id, name, filter_definition (JSON), owner_id
  - supports: FR-NTF-02 (targeting)

- Student (existing) — assumed present in system
  - student_id, name, email, line_id, enrolled_faculty, year
  - supports: FR-NTF-02

## 4. API / หน้าจอ
- POST /api/notifications
  - input: {title, body, publish_at, expires_at, channels, target: {segment_id or csv}} 
  - output: {notification_id, status}
  - รองรับ: FR-NTF-01, FR-NTF-02

- GET /api/notifications/{id}
  - output: Notification details (title, body, author, created_at, attachments link)
  - รองรับ: FR-NTF-03

- POST /api/notifications/{id}/enqueue-send
  - input: {channels?}
  - action: enqueue worker เพื่อส่งไปยังแต่ละ student ตาม target
  - รองรับ: FR-NTF-01, FR-NTF-02, FR-NTF-04

- GET /api/students/{id}/notifications
  - output: list of in-app notifications
  - รองรับ: FR-NTF-02, FR-NTF-03

- Saved Segments UI: GET/POST /api/segments, POST /api/segments/upload-csv
  - รองรับ: FR-NTF-02

### หน้าจอ (UI)
- Create Notification (Dynamic Filters, channels, preview, upload CSV)
- Manage Saved Segments (create, edit, apply)
- Student Notification Center (list + detail)

## 5. ตารางตรวจ Constraints
Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ
---|---|---
No specific business rule (จาก spec) | ใช้เพื่อกำหนดว่าไม่มีข้อจำกัดเพิ่มเติมที่ห้ามเก็บข้อมูล — แปลว่า plan ใช้ default storage และ logging | ใช้แล้ว

## 6. แผนทดสอบจาก Acceptance Criteria
AC ID | ชื่อ test | ทดสอบอย่างไร
---|---|---
AC-NTF-01 | test_AC_NTF_01_send_notification | สร้าง notification ผ่าน API แล้วเรียก /enqueue-send; ตรวจสอบว่า NotificationDeliveryAttempt ถูกสร้างและมีงาน enqueue สำหรับ students ที่เกี่ยวข้อง (mock external channels)
AC-NTF-02 | test_AC_NTF_02_show_details | ส่ง notification ให้ student (in-app) แล้วเรียก GET /api/notifications/{id} และ UI แสดง title/body/author/created_at
AC-NTF-03 | test_AC_NTF_03_retry_and_fallback | จำลอง failure ของ channel; ตรวจสอบว่า system พยายาม retry ตาม policy (3 attempts, exponential backoff) และบันทึก status เป็น failed แล้วพยายามช่องทางสำรอง

## 7. ลำดับงาน (5-10 ขั้น)
1. ออกแบบ DB schema (Notification, DeliveryAttempt, SavedSegment) — FR-NTF-01, FR-NTF-04
2. พัฒนา API สร้าง/อ่าน Notification และ endpoints สำหรับ segments — FR-NTF-01, FR-NTF-03
3. พัฒนา worker/queue สำหรับการส่งและ retry logic — FR-NTF-04
4. พัฒนาหน้า Create Notification (Dynamic Filters + CSV upload) และ Saved Segments UI — FR-NTF-02
5. ผสานการเชื่อมต่อกับ LINE/Email providers (stub/mocks ใน dev) — FR-NTF-01
6. เพิ่ม logging/audit และ dashboard ตรวจสอบการส่งล้มเหลว — NFR-REL-02, FR-NTF-04
7. เขียน automated tests ตาม ACs และ integration tests สำหรับ retry/fallback — AC-NTF-01..03

## 8. สิ่งที่ยังไม่ทำ
Open Questions ใน `spec.md`: ไม่มีหัวข้อ Open Questions คงค้าง (ทุกคำถามสำคัญได้รับคำตอบและถูกย้ายเป็น ASM) 
ส่วนที่เกี่ยวข้องกับข้อนี้จะยังไม่สร้างจนกว่าจะได้คำตอบ

---

ไฟล์นี้เชื่อมกลับไปยัง: `specs/008-notification/spec.md` (SPEC-NTF-001)
