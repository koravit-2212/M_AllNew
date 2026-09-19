# แผนงาน: เข้าใช้บริการห้องสมุด (Access)

## 1. สรุปแนวทาง
- ฟีเจอร์นี้ให้ผู้ใช้แสดงบัตรนักศึกษาหรือ QR Code ที่ประตูทางเข้าเพื่อยืนยันตัวตนและเข้าห้องสมุดได้ โดยระบบจะตรวจสอบสิทธิ์และบันทึกการเข้าใช้บริการแบบ Real-time
- ผู้ใช้หลักคือ นักศึกษา บุคลากร และบุคคลที่มหาวิทยาลัยหรือห้องสมุดกำหนดสิทธิ์ให้ใช้บริการ
- ระบบจะมีชั้นหน้า Web kiosk สำหรับสแกนบัตร/QR และชั้นหลัง API สำหรับตรวจสอบข้อมูลผู้ใช้และอัปเดตสถิติผู้ใช้ในอาคาร
- การทำงานจะเน้นความปลอดภัยและความถูกต้อง: ปฏิเสธเมื่อไม่ตรวจสอบได้, จัดกลุ่มสถานะตามสาเหตุ, และบันทึก Audit Log สำหรับกรณีเจ้าหน้าที่ตรวจสอบด้วยมือ
- ขอบเขตนี้ใช้ spec.md เป็นแหล่งความจริง และยึดตาม Draft v2 ที่มีผลลัพธ์ Clarify แล้ว

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| React + Vite สำหรับหน้า kiosk / เครื่องอ่านประตูทางเข้า | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ UI การสแกนและแสดงสถานะการยืนยันตัวตน |
| Python FastAPI สำหรับ API ตรวจสอบสิทธิ์และจัดการ access log | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับบริการตรวจสอบข้อมูลและอัปเดต Real-time status |
| PostgreSQL สำหรับเก็บ log, status, และข้อมูลสมาชิกที่จำเป็น | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้เพื่อความเสถียรและอัปเดตสถานะพร้อมกันได้ 500 รายการ |
| HTTPS ทั้งหมดสำหรับการสื่อสาร | CON-SEC-01 | บังคับใช้ทุกการเชื่อมต่อของระบบ |
| ระบบบัตรนักศึกษาภายนอก (UC-02) | IF-STD-01, IF-STD-02 | ฟังก์ชันเชื่อมต่อแบบ synchronous และต้องจัดการกรณี timeout / ไม่ตอบ |

## 3. โมเดลข้อมูล

| Entity | ฟิลด์หลัก | รองรับ FR |
|---|---|---|
| MemberProfile | member_id, type, status, eligibility_status, last_verified_at | FR-ACC-01, FR-ACC-02 |
| AccessEvent | access_event_id, member_id, scan_method, scanned_at, result_status, actor_type, staff_id, audit_note | FR-ACC-03, FR-ACC-04, FR-ACC-05, FR-ACC-06 |
| FacilityOccupancy | facility_id, current_occupancy, updated_at | FR-ACC-03 |
| ManualVerificationAudit | audit_id, event_id, verified_by_staff_id, verification_reason, verified_at, approved_by | FR-ACC-06 |
| ScanResult | scan_id, input_type, read_status, error_code, message, is_allowed | FR-ACC-04, FR-ACC-05 |

หมายเหตุ:
- ไม่เก็บเลขประจำตัวประชาชนหรือข้อมูลบัตรประชาชนแบบละเอียดเพิ่มเติม เพราะ spec ระบุว่าเป็นข้อมูลส่วนบุคคลที่ต้องจัดการตามนโยบายของมหาวิทยาลัยและกฎหมาย และไม่ได้มีการระบุให้เก็บฟิลด์เฉพาะดังกล่าวใน FR/Constraint
- Entity ทั้งหมดมีการยึดจากข้อมูลที่จำเป็นเพื่อให้ระบบยืนยันสิทธิ์และบันทึก Audit Log ได้โดยไม่เกินขอบเขตที่กำหนด

## 4. API / หน้าจอ

- Web page: Kiosk Entry Screen — แสดงปุ่ม/พื้นที่สแกน QR Code หรือบัตรนักศึกษา และแสดงผลลัพธ์แบบ status code
  - รองรับ: FR-ACC-01, FR-ACC-04, FR-ACC-05
- POST /api/access/scan — input: { scanMethod, qrCodeOrCardId } / output: { status, allowed, message, eventId }
  - รองรับ: FR-ACC-01, FR-ACC-04, FR-ACC-05
- GET /api/access/status — output: { currentOccupancy, lastUpdatedAt }
  - รองรับ: FR-ACC-03
- POST /api/access/verify-manual — input: { eventId, staffId, reason, manualApproved } / output: { auditId, approved, message }
  - รองรับ: FR-ACC-06
- POST /api/access/exit — input: { memberId, confirmationToken } / output: { updatedOccupancy, status }
  - รองรับ: FR-ACC-03
- GET /api/access/audit-log — output: { entries[] }
  - รองรับ: FR-ACC-06

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| IF-STD-01 | การออกแบบ integration layer สำหรับระบบบัตรนักศึกษาภายนอกใน POST /api/access/scan และ validation service | ใช้แล้ว |
| IF-STD-02 | Flow ปฏิเสธการเข้าเมื่ออาจไม่ตรวจสอบสิทธิ์ได้ พร้อมข้อความ "ลองใหม่หรือติดต่อเจ้าหน้าที่" และ fallback บนหน้า kiosk | ใช้แล้ว |
| DOM-PRV-01 | บันทึกข้อมูลส่วนบุคคลเฉพาะที่จำเป็น, จำกัดการเปิดเผย, และจัดเก็บ Audit Log อย่างมีสิทธิ์ | ใช้แล้ว |
| CON-IDN-01 | หน้า kiosk ใช้เฉพาะ QR Code หรือบัตรนักศึกษา ที่ได้รับจากแหล่งยืนยันตัวตนเท่านั้น | ใช้แล้ว |
| CON-ELG-01 | MemberProfile และ eligibility_status ใช้ในการตัดสินใจอนุญาตหรือปฏิเสธตามข้อมูลสมาชิกหรือฐานข้อมูลที่ห้องสมุดกำหนด | ใช้แล้ว |
| CON-SEC-01 | ทุก endpoint ใช้ HTTPS และส่งผ่าน reverse proxy / gateway ที่บังคับ TLS | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-ACC-01 | test_AC_ACC_01_successful_access_scan | จำลอง QR Code ที่ถูกต้องและสิทธิ์ valid, ตรวจว่าระบบอนุญาตให้เข้า บันทึก AccessEvent และอัปเดต currentOccupancy |
| AC-ACC-02 | test_AC_ACC_02_denied_without_eligibility | จำลองผู้ใช้ที่ไม่มีสิทธิ์, ตรวจว่าระบบไม่อนุญาตและแสดงผล "ไม่มีสิทธิ์" |
| AC-ACC-03 | test_AC_ACC_03_scan_read_failure | จำลองเครื่องอ่านไม่สามารถอ่าน QR Code, ตรวจว่าระบบแสดง "ไม่สามารถอ่านข้อมูล" และไม่บันทึก AccessEvent |
| AC-ACC-04 | test_AC_ACC_04_500_concurrent_users | จำลองผู้ใช้งานพร้อมกัน 500 คน, ตรวจว่าระบบยังทำงานได้ภายใน 2 วินาทีสำหรับ validation และ update occupancy |

## 7. ลำดับงาน

1. กำหนดโครงสร้าง UI kiosk และ API contract สำหรับ scan flow (FR-ACC-01, FR-ACC-04, FR-ACC-05)
2. สร้าง integration layer สำหรับเชื่อมระบบบัตรนักศึกษาภายนอกและจัดการ timeout / no-response (IF-STD-01, IF-STD-02, FR-ACC-01)
3. สร้าง service ตรวจสอบสิทธิ์และ member eligibility จากข้อมูลสมาชิกหรือฐานข้อมูลห้องสมุด (FR-ACC-02, CON-ELG-01)
4. สร้าง logic บันทึก AccessEvent และอัปเดต FacilityOccupancy สำหรับการเข้า/ออก (FR-ACC-03)
5. สร้าง flow สำหรับสถานะที่แยกตามสาเหตุ ไม่สามารถอ่าน / ไม่พบข้อมูล / ไม่มีสิทธิ์ (FR-ACC-04, FR-ACC-05)
6. เพิ่มระบบ manual verification สำหรับเจ้าหน้าที่ที่มีสิทธิ์ พร้อม Audit Log (FR-ACC-06)
7. ทำการทดสอบการรับโหลด 500 คนพร้อมกันและจับเวลา validation/update ให้ตรง NFR-PRF-02 (AC-ACC-04)
8. ทดสอบกรณี success / denied / read fail และตรวจสอบความถูกต้องของ audit trail (AC-ACC-01, AC-ACC-02, AC-ACC-03)

## 8. สิ่งที่ยังไม่ทำ

- ไม่มี Open Questions ใน spec ปัจจุบัน จึงไม่มีข้อใดที่ต้องรอคำตอบก่อนสร้างฟีเจอร์นี้
- หากมีการเปิด Q ใหม่ในอนาคต ส่วนที่เกี่ยวข้องกับข้อนั้นจะยังไม่สร้างจนกว่าจะได้คำตอบ

---

## หมายเหตุการใช้งาน
- แผนนี้พัฒนาให้สอดคล้องกับ spec.md ใน Draft v2 เท่านั้น
- ข้อที่ยังไม่สามารถวัดค่าชัดเจน เช่น latency ระหว่างระบบภายนอกกับระบบภายใน จะถูกจัดการผ่าน test และ observability เมื่อเริ่มพัฒนาจริง
