# แผนงาน: จอง/ใช้พื้นที่ในห้องสมุด (Space Booking)

## 1. สรุปแนวทาง
- ฟีเจอร์นี้ให้ผู้ใช้ที่มีสิทธิ์เลือกพื้นที่และช่วงเวลาสำหรับอ่านหนังสือหรือทำงาน และยืนยันการจองให้ระบบจัดสรรพื้นที่ได้อย่างมีประสิทธิภาพ
- ผู้ใช้หลักคือ นักศึกษา บุคลากร หรือผู้ที่ได้รับอนุญาตจากห้องสมุด/มหาวิทยาลัย ตาม CON-ELG-01
- ระบบจะมีหน้า Web UI สำหรับเลือกพื้นที่และช่วงเวลา พร้อม API/backend เพื่อตรวจสอบความว่างและบันทึกการจองแบบ atomic transaction
- การออกแบบจะเน้นการป้องกันการจองซ้อนและการแสดงผลที่ชัดเจนเมื่อพื้นที่ไม่ว่าง เพื่อให้การจองเกิดขึ้นได้เพียงหนึ่งรายการต่อพื้นที่/เวลา
- ขอบเขตนี้ยึดตาม spec.md รุ่น Draft v2 และอ้างอิงทุกความต้องการไปยัง FR / CON / AC ที่มีอยู่ใน spec

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| React + Vite สำหรับหน้าเลือกพื้นที่และยืนยันการจอง | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ UI บนเว็บทั้งคอมพิวเตอร์และมือถือ |
| Python FastAPI สำหรับ API ตรวจสอบความว่างและบันทึกการจอง | ทีมเลือกเอง ไม่ได้มาจาก spec | รองรับธุรกิจ logic และ atomic reservation flow |
| PostgreSQL สำหรับเก็บข้อมูลการจองและข้อมูลพื้นที่ | ทีมเลือกเอง ไม่ได้มาจาก spec | เหมาะสำหรับ transaction ที่ต้องป้องกัน race condition |
| Transaction/locking model ในฐานข้อมูล | CON-CONC-01 | ใช้เพื่อป้องกันการจองซ้อนเมื่อหลายคนยืนยันพร้อมกัน |
| การยืนยันสิทธิ์ผู้ใช้ตามข้อมูลสมาชิก/สิทธิ์ที่ห้องสมุดกำหนด | CON-ELG-01 | ตรวจสอบก่อนให้ทำการจอง |

## 3. โมเดลข้อมูล

| Entity | ฟิลด์หลัก | รองรับ FR |
|---|---|---|
| Space | space_id, space_type, facility_name, capacity, status, availability_policy | FR-BKG-01 |
| SpaceTimeSlot | slot_id, space_id, date, start_time, end_time, status | FR-BKG-01, FR-BKG-02 |
| Reservation | reservation_id, user_id, space_id, slot_id, reservation_time, status, message | FR-BKG-02, FR-BKG-03, FR-BKG-04 |
| UserProfile | user_id, user_type, eligibility_status, verified_at | FR-BKG-01, CON-ELG-01 |
| BookingAuditLog | log_id, reservation_id, action, performed_at, result, reason | FR-BKG-03, FR-BKG-04 |

หมายเหตุ:
- Entity จะเก็บเฉพาะข้อมูลที่จำเป็นสำหรับการคัดเลือกพื้นที่ การตรวจสอบว่าง และบันทึกการจอง ตาม spec
- ไม่กำหนดฟิลด์ที่เก็บข้อมูลพิเศษนอกเหนือจากนี้ เพราะ spec ไม่ได้ระบุไว้ และไม่อนุญาตให้เพิ่มความต้องการที่เกินขอบเขต

## 4. API / หน้าจอ

- Web page: Reservation Selection Screen — แสดงพื้นที่ว่างและช่วงเวลาให้ผู้ใช้เลือก
  - รองรับ: FR-BKG-01
- GET /api/spaces/available — output: { spaces[], slots[] }
  - รองรับ: FR-BKG-01
- POST /api/reservations/check-availability — input: { spaceId, date, startTime, endTime } / output: { available, reason }
  - รองรับ: FR-BKG-02
- POST /api/reservations — input: { userId, spaceId, date, startTime, endTime } / output: { reservationId, status, message }
  - รองรับ: FR-BKG-02, FR-BKG-03, FR-BKG-04
- GET /api/reservations/{reservationId} — output: { reservationStatus, spaceInfo, slotInfo }
  - รองรับ: FR-BKG-03
- Web page: Reservation Result Screen — แสดงผลสำเร็จหรือผลไม่ว่างพร้อมคำแนะนำให้เลือกพื้นที่/เวลาอื่น
  - รองรับ: FR-BKG-03, FR-BKG-04

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| CON-ELG-01 | ตรวจสอบสิทธิ์ผู้ใช้ก่อนเปิดตัวเลือกพื้นที่และก่อนสร้าง reservation | ใช้แล้ว |
| CON-CONC-01 | ใช้ transaction/locking ระหว่าง check availability กับ insert reservation เพื่อป้องกัน race condition | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-BKG-01 | test_AC_BKG_01_display_available_spaces | จำลองพื้นที่เปิดให้บริการและตรวจว่าระบบแสดงรายชื่อพื้นที่พร้อมช่วงเวลาที่ว่างให้เลือก |
| AC-BKG-02 | test_AC_BKG_02_successful_reservation | จำลองพื้นที่ว่างและยืนยันการจอง ตรวจว่าระบบตรวจสอบความว่างแล้วบันทึก reservation และแสดงผลสำเร็จ |
| AC-BKG-03 | test_AC_BKG_03_unavailable_space_rejected | จำลองพื้นที่/ช่วงเวลาที่ไม่ว่าง ตรวจว่าระบบไม่สร้าง reservation เพิ่ม และแจ้งให้เลือกพื้นที่หรือเวลาอื่น |
| AC-BKG-04 | test_AC_BKG_04_concurrent_booking_prevented | จำลองสองผู้ใช้ยืนยันพร้อมกันบนพื้นที่/เวลาเดียวกัน ตรวจว่ามีเพียง 1 รายการสำเร็จ และอีกรายการได้รับข้อความพื้นที่ไม่ว่าง |

## 7. ลำดับงาน

1. จัดทำ UI สำหรับการเลือกพื้นที่และช่วงเวลา พร้อมติดต่อ API ดึงข้อมูลพื้นที่ว่าง (FR-BKG-01)
2. สร้าง service ตรวจสอบสิทธิ์ผู้ใช้ตาม CON-ELG-01 ก่อนอนุญาตสมัครการจอง (FR-BKG-01, CON-ELG-01)
3. สร้าง logic ตรวจสอบความว่างใน slot ที่เลือก พร้อมแสดงสถานะพร้อมใช้/ไม่พร้อมใช้งาน (FR-BKG-02)
4. สร้าง transaction สำหรับ check availability + insert reservation เพื่อป้องกันการจองซ้อน (FR-BKG-02, FR-BKG-03, CON-CONC-01)
5. สร้างหน้าและบริการแจ้งผลสำเร็จเมื่อจองได้ และแจ้งให้เลือกพื้นที่/เวลาอื่นเมื่อไม่ว่าง (FR-BKG-03, FR-BKG-04)
6. ทดสอบกรณี success, unavailable, และ concurrent booking ตาม AC-BKG-01 ถึง AC-BKG-04
7. ตรวจสอบผลลัพธ์และความถูกต้องตาม spec และปรับข้อความ/ error handling ให้ตรงกับคำยืนยันการจองตาม UX

## 8. สิ่งที่ยังไม่ทำ

- ไม่มี Open Questions ใน spec ปัจจุบัน จึงไม่มีข้อใดที่ต้องรอคำตอบก่อนเริ่มพัฒนาในฟีเจอร์นี้
- หากมีคำถามใหม่เกิดขึ้นในอนาคต ส่วนที่เกี่ยวข้องจะยังไม่สร้างจนกว่าจะได้รับคำตอบที่ชัดเจน

---

## หมายเหตุเพิ่มเติม
- แผนนี้ถูกสร้างจาก spec.md ใน Draft v2 เท่านั้น
- ไม่ได้เพิ่ม FR หรือ AC ใด ๆ ที่ไม่มีใน spec
- ทุกชิ้นงานในแผนต้องสามารถอ้างกลับไปหา FR / CON / AC ที่ระบุไว้ใน spec ได้อย่างชัดเจน
