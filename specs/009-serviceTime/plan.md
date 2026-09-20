# Plan for Feature: ตรวจสอบเวลาเปิดให้บริการ (Operating Hours)

## 1. สรุปแนวทาง (5 บรรทัด)
- ฟีเจอร์นี้ให้นักศึกษาเปิดดูข้อมูลเวลาทำการของห้องสมุดเพื่อวางแผนการเข้าใช้บริการล่วงหน้า
- ผู้ใช้หลักคือนักศึกษาและเจ้าหน้าที่ห้องสมุดที่จัดเก็บข้อมูลเวลาเปิด-ปิด
- แนวทางคือเก็บข้อมูลตารางเวลาปกติและตารางการเปลี่ยนแปลงชั่วคราวแยกกัน แล้วคำนวณข้อมูลที่มีผลบังคับใช้อยู่ ณ เวลานั้นก่อนแสดงผล
- ระบบจะแสดงข้อมูลปัจจุบันแบบหลักและมี Badge สถานะสำหรับวันหยุดพิเศษ/ปรับเวลา หากต้องการดูภาพรวมปกติให้ใช้ปุ่มหรือส่วนขยายแยกต่างหาก
- เป้าหมายหลักคือให้ข้อมูลสอดคล้องกับประกาศมหาวิทยาลัยและไม่ให้ผู้ใช้เข้าใจผิดเมื่อมีการเปลี่ยนแปลงชั่วคราว

## 2. เทคโนโลยีที่ใช้
| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับหน้า “เวลาเปิดให้บริการ” และการแสดง Badge/expand table |
| Backend: Python FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ API ดึงข้อมูลเวลาเปิด-ปิดปัจจุบันและตารางปกติ |
| Database: PostgreSQL | ทีมเลือกเอง ไม่ได้มาจาก spec | เก็บตารางเวลาปกติและ override สำหรับวันหยุดพิเศษ/การเปลี่ยนแปลงชั่วคราว |
| UI state: client-side data composition | FR-SCH-01 | ระบบคำนวณข้อมูลปัจจุบันจากตารางปกติ + override ก่อน render |
| Data validation: server-side validation against effective schedule | CON-SCH-01 | ต้องมั่นใจว่าข้อมูลที่ส่งออกตรงตามประกาศมหาวิทยาลัย |

## 3. โมเดลข้อมูล
| Entity | ฟิลด์หลัก | รองรับ FR |
|---|---|---|
| LibraryOperatingSchedule | schedule_id, day_of_week, open_time, close_time, is_active, effective_from, effective_to, source_type | FR-SCH-01 |
| LibraryScheduleOverride | override_id, title, override_type, effective_from, effective_to, open_time, close_time, reason, badge_label, is_active | FR-SCH-01 |
| LibraryHoursView | effective_schedule_id, display_label, status_type, is_regular_view, regular_schedule_id, override_id | FR-SCH-01 |

หมายเหตุ:
- ตารางปกติจะเก็บเวลาเปิด-ปิดตามปกติของแต่ละวันในสัปดาห์
- ตาราง override จะเก็บวันหยุดพิเศษหรือการปรับเปลี่ยนเวลาให้บริการชั่วคราวที่มีผลบังคับใช้อยู่
- ข้อมูลแสดงผลจะคำนวณให้เลือก override ที่มีผลบังคับใช้อยู่ ณ ขณะนั้น และแสดงตารางปกติผ่านปุ่ม/ส่วนขยายแทนการแทนที่คงที่
- ไม่มีการเก็บข้อมูลบัตรประชาชนหรือข้อมูลที่ไม่จำเป็นต่อฟีเจอร์นี้ตาม spec

## 4. API / หน้าจอ
- GET /api/library-hours/current
  - input: none
  - output: {status, schedule, badge, regular_schedule_available}
  - รองรับ: FR-SCH-01

- GET /api/library-hours/regular
  - input: none
  - output: {weekly_schedule}
  - รองรับ: FR-SCH-01

- GET /api/library-hours/overrides
  - input: {date}
  - output: [{override_id, title, type, effective_from, effective_to, reason}]
  - รองรับ: FR-SCH-01

- หน้า: เวลาเปิดให้บริการ
  - แสดงข้อมูลปัจจุบันแบบผนวก badge และ allow expand regular schedule
  - รองรับ: FR-SCH-01, AC-SCH-01

## 5. ตารางตรวจ Constraints
| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| CON-SCH-01 | ใช้ใน Business Rule validation: API และ service layer ต้องคัดเลือกข้อมูลที่มีผลบังคับใช้อยู่ ณ เวลานั้น และตรวจสอบให้ตรงกับประกาศมหาวิทยาลัยก่อนส่งให้ UI | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria
| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-SCH-01 | test_AC_SCH_01_display_current_hours_with_override_badge | จำลองข้อมูลปกติและ override ที่มีผลบังคับใช้อยู่ แล้วเรียก API /api/library-hours/current ตรวจสอบว่าระบบ return schedule ปัจจุบัน, มี badge แจ้งวันหยุด/ปรับเวลา และมี field สำหรับแสดงตารางปกติแยกต่างหาก |

## 7. ลำดับงาน
1. ออกแบบ schema สำหรับตารางปกติและ override สำหรับวันหยุด/ปรับเวลา — FR-SCH-01, CON-SCH-01
2. สร้าง API ดึงข้อมูลปัจจุบันและตารางปกติ — FR-SCH-01
3. implement logic คำนวณข้อมูล “ที่มีผลบังคับใช้อยู่ ณ เวลานั้น” โดยให้ override มี priority สูงกว่า schedule ปกติ — FR-SCH-01, CON-SCH-01
4. สร้าง UI หน้าเวลาเปิดให้บริการพร้อม Badge และปุ่มดูตารางปกติ — FR-SCH-01, AC-SCH-01
5. ทดสอบ flow เมื่อมี override และเมื่อไม่มี override — FR-SCH-01, AC-SCH-01
6. ตรวจสอบความสอดคล้องกับประกาศมหาวิทยาลัยและบันทึกประวัติการแก้ไขในระบบ (ถ้าจำเป็น) — CON-SCH-01

## 8. สิ่งที่ยังไม่ทำ
- Open Questions ใน spec.md: ไม่มีในเวอร์ชัน Draft v2 ปัจจุบัน
- ส่วนที่เกี่ยวข้องกับข้อนี้จะยังไม่สร้างจนกว่าจะได้คำตอบ หากมีการเปลี่ยนแปลงในอนาคต เช่น กรณีวันหยุดพิเศษมีหลายรูปแบบ หรือการจัดการประกาศที่เปลี่ยนแปลงไม่ทันที

---
ไฟล์นี้เชื่อมกลับไปยัง: specs/009-serviceTime/spec.md (SPEC-SCH-001)
