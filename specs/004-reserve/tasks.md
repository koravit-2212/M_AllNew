# tasks: จอง/ใช้พื้นที่ในห้องสมุด (Space Booking)

- Feature: จอง/ใช้พื้นที่ในห้องสมุด
- Spec ID: SPEC-BKG-002 (`specs/004-reserve/spec.md` Draft v2)
- อ้างอิง: `specs/004-reserve/plan.md`
- วันที่: 2569-11-12

สรุป
1. มี 5 เฟส (เฟส 0 ถึงเฟส 4) รวม 9 task
2. task ที่ต้องรอ Open Questions: 0 task (spec ไม่มี Q-xx ค้าง แต่มี "ข้อเสนอคำถาม" 3 ข้อท้ายไฟล์ที่ทีมควรตอบก่อนเฟส 2)
3. เฟสแรกที่ลองใช้งานได้จริงคือเฟส 1 (เห็นรายการพื้นที่และช่วงเวลา) ส่วนเฟส 0 ลองได้แค่เมนูสลับหน้า

หมายเหตุทางเทคนิค (ทีมเลือกเอง ไม่ได้มาจาก spec)
- plan.md เลือก PostgreSQL แต่โค้ดที่มีอยู่ของ 003 ใช้ข้อมูลตัวอย่างในหน่วยความจำ (ไม่ต่อฐานข้อมูลจริง) task ชุดนี้ทำตามแนวทางเดียวกับ 003 คือเก็บพื้นที่ ช่วงเวลา และการจองในหน่วยความจำ และทำ CON-CONC-01 ด้วย lock ใน process ถ้าทีมต้องการต่อ PostgreSQL จริงต้องเพิ่ม task ภายหลัง
- spec.md ไม่มีหมวด "หน้าจอ (UI)" จึงยังไม่มีข้อความที่ระบุว่า "ต้องตรง" กับ mockup task หน้าจอใช้ข้อความจาก `mockups/UI-BKG-01-space-booking.html` เป็นแนวทาง และทีมควรตรวจด้วยตา

## เฟส 0: ฐานราก (ไม่มี AC เป็นงานพื้นฐาน)

### T-01 สร้างข้อมูลพื้นที่และช่วงเวลาตัวอย่าง พร้อมที่เก็บการจอง
- รองรับ: FR-BKG-01, CON-CONC-01 (ที่เก็บการจองมี lock สำหรับใช้ในเฟส 2 ถึง 4), ASM-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-03, T-05
- ไฟล์ที่แตะ: `backend/app/config.py`, `backend/app/models/space.py`, `backend/tests/test_BKG_T01_space_store.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: `test_BKG_T01_space_store.py` ผ่าน โดยยืนยันว่าข้อมูลตัวอย่างมีพื้นที่อย่างน้อย 2 แห่ง และแต่ละแห่งมีช่วงเวลาให้เลือก
- สถานะ: เสร็จ รอทีมตรวจ

### T-02 เพิ่มเมนูไปหน้าจองพื้นที่ใน App.jsx โดยไม่ลบหน้าเดิม
- รองรับ: FR-BKG-01 (ขั้น "นักศึกษาเลือกบริการพื้นที่"), NFR-USB-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-04
- ไฟล์ที่แตะ: `frontend/src/App.jsx`, `frontend/src/pages/SpaceBookingPage.jsx`, `frontend/src/__tests__/App.test.jsx`
- แบบหน้าจอ: UI-BKG-01 `mockups/UI-BKG-01-space-booking.html` (เฉพาะแถบชื่อหน้า "จองพื้นที่ในห้องสมุด")
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: `App.test.jsx` ผ่าน กดเมนู "จองพื้นที่" แล้วเห็นหัวข้อ "จองพื้นที่ในห้องสมุด" และกดกลับเมนู "หนังสือ" แล้วเห็นหน้าค้นหาเดิม
- สถานะ: เสร็จ รอทีมตรวจ

#### จุดตรวจเฟส 0
- test ที่ต้องผ่านทั้งหมด: `test_BKG_T01_space_store.py`, `App.test.jsx` และ test เดิมของ 003 ทั้งหมดต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเอง (ไม่มี AC):
  Given เปิดเว็บที่ port 5173
  When กดเมนู "จองพื้นที่" แล้วกดเมนู "หนังสือ"
  Then เห็นหัวข้อ "จองพื้นที่ในห้องสมุด" และกลับมาเห็นหน้าค้นหาหนังสือเดิมได้
- ยังขาด: ไม่มี

## เฟส 1: เห็นพื้นที่ที่ใช้งานได้พร้อมช่วงเวลา (AC-BKG-01)

### T-03 สร้าง API GET /api/spaces/available และลงทะเบียน router
- รองรับ: FR-BKG-01
- ตรวจด้วย: AC-BKG-01
- ไฟล์ที่แตะ: `backend/app/api/spaces.py`, `backend/app/main.py`, `backend/tests/test_AC_BKG_01_available_spaces.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: `test_AC_BKG_01_display_available_spaces` ผ่าน (API คืนรายการพื้นที่พร้อมช่วงเวลาและสถานะว่าง/เต็มของแต่ละช่วง)
- สถานะ: เสร็จ รอทีมตรวจ

### T-04 แสดงรายการพื้นที่และช่วงเวลาให้เลือกในหน้าจองพื้นที่
- รองรับ: FR-BKG-01, NFR-USB-01
- ตรวจด้วย: AC-BKG-01
- ไฟล์ที่แตะ: `frontend/src/api/client.js`, `frontend/src/pages/SpaceBookingPage.jsx`, `frontend/src/__tests__/SpaceBookingPage.test.jsx`
- แบบหน้าจอ: UI-BKG-01 `mockups/UI-BKG-01-space-booking.html` (สถานะปกติ AC-BKG-01)
- ต้องทำหลัง: T-02, T-03
- เสร็จเมื่อ: test หน้าจอ AC-BKG-01 ผ่าน (ใช้ client จำลอง เห็นชื่อพื้นที่ ช่วงเวลา และป้าย "ว่าง"/"เต็ม")
- สถานะ: เสร็จ รอทีมตรวจ

#### จุดตรวจเฟส 1
- test ที่ต้องผ่านทั้งหมด: `test_AC_BKG_01_*` (หลังบ้าน), `SpaceBookingPage.test.jsx` (AC-BKG-01) และ test ของเฟส 0 กับ 003 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-BKG-01:
  Given ใช้ข้อมูลพื้นที่ตัวอย่างจาก `config.py`
  When กดเมนู "จองพื้นที่"
  Then เห็นรายการพื้นที่ที่ใช้งานได้ และเมื่อเลือกพื้นที่ เห็นช่วงเวลาให้เลือกพร้อมสถานะว่าง/เต็ม
- ยังขาด: ไม่มี

## เฟส 2: จองสำเร็จ (AC-BKG-02)

### T-05 สร้าง API ตรวจความว่างและบันทึกการจองแบบ atomic พร้อมตรวจสิทธิ์ผู้จอง
- รองรับ: FR-BKG-02, FR-BKG-03, CON-CONC-01, CON-ELG-01
- ตรวจด้วย: AC-BKG-02
- ไฟล์ที่แตะ: `backend/app/config.py`, `backend/app/services/reservation_service.py`, `backend/app/api/reservations.py`, `backend/app/main.py`, `backend/tests/test_AC_BKG_02_successful_reservation.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: `test_AC_BKG_02_successful_reservation` ผ่าน (POST /api/reservations/check-availability ตอบว่าว่าง, POST /api/reservations บันทึกการจองและตอบสำเร็จ, GET /api/reservations/{id} อ่านการจองกลับมาได้)
- สถานะ: พร้อมทำ (ทีมควรตอบข้อเสนอคำถาม ข้อ 1 ก่อนเริ่ม)

### T-06 ทำขั้น "ยืนยัน" และหน้าผล "จองสำเร็จ"
- รองรับ: FR-BKG-03, NFR-USB-01
- ตรวจด้วย: AC-BKG-02
- ไฟล์ที่แตะ: `frontend/src/api/client.js`, `frontend/src/pages/SpaceBookingPage.jsx`, `frontend/src/__tests__/SpaceBookingPage.test.jsx`
- แบบหน้าจอ: UI-BKG-01 `mockups/UI-BKG-01-space-booking.html` (สถานะจองสำเร็จ AC-BKG-02)
- ต้องทำหลัง: T-04, T-05
- เสร็จเมื่อ: test หน้าจอ AC-BKG-02 ผ่าน (กดยืนยันแล้วเห็น "จองสำเร็จ" พร้อมพื้นที่ วันที่ และเวลา)
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 2
- test ที่ต้องผ่านทั้งหมด: `test_AC_BKG_02_*`, test หน้าจอ AC-BKG-02 และ test ของเฟส 0 ถึง 1 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-BKG-02:
  Given เปิดหลังบ้านใหม่ (ข้อมูลตัวอย่างยังไม่มีการจอง) และเลือกพื้นที่กับช่วงเวลาที่ขึ้น "ว่าง"
  When กด "ถัดไป" แล้วกดยืนยันการจอง
  Then เห็น "จองสำเร็จ" พร้อมพื้นที่ วันที่ และเวลาที่เลือก และเมื่อกลับไปหน้าเลือก ช่วงเวลานั้นขึ้น "เต็ม"
- ยังขาด: ไม่มี

## เฟส 3: พื้นที่ไม่ว่าง (AC-BKG-03)

### T-07 ปฏิเสธการจองช่วงเวลาที่ไม่ว่างโดยไม่สร้างรายการซ้อน
- รองรับ: FR-BKG-02, FR-BKG-04, CON-CONC-01
- ตรวจด้วย: AC-BKG-03
- ไฟล์ที่แตะ: `backend/app/services/reservation_service.py`, `backend/app/api/reservations.py`, `backend/tests/test_AC_BKG_03_unavailable_space_rejected.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-05
- เสร็จเมื่อ: `test_AC_BKG_03_unavailable_space_rejected` ผ่าน (จองช่วงที่ถูกจองแล้วได้ผลไม่ว่าง และจำนวนการจองไม่เพิ่ม)
- สถานะ: พร้อมทำ

### T-08 แสดงสถานะ "พื้นที่ไม่ว่าง" และปุ่มกลับไปเลือกใหม่
- รองรับ: FR-BKG-04, NFR-USB-01
- ตรวจด้วย: AC-BKG-03
- ไฟล์ที่แตะ: `frontend/src/pages/SpaceBookingPage.jsx`, `frontend/src/__tests__/SpaceBookingPage.test.jsx`
- แบบหน้าจอ: UI-BKG-01 `mockups/UI-BKG-01-space-booking.html` (สถานะพื้นที่ไม่ว่าง AC-BKG-03)
- ต้องทำหลัง: T-06, T-07
- เสร็จเมื่อ: test หน้าจอ AC-BKG-03 ผ่าน (เห็น "พื้นที่ไม่ว่างในช่วงเวลานี้" และปุ่ม "กลับไปเลือกพื้นที่/เวลาใหม่")
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 3
- test ที่ต้องผ่านทั้งหมด: `test_AC_BKG_03_*`, test หน้าจอ AC-BKG-03 และ test ของเฟส 0 ถึง 2 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-BKG-03:
  Given เปิดเว็บ 2 แท็บ เลือกพื้นที่และช่วงเวลาเดียวกันที่ขึ้น "ว่าง" ทั้งสองแท็บ แล้วจองให้สำเร็จในแท็บแรก
  When กดยืนยันการจองในแท็บที่สอง
  Then แท็บที่สองเห็น "พื้นที่ไม่ว่างในช่วงเวลานี้" กดกลับไปเลือกใหม่ได้ และช่วงเวลานั้นมีการจองเพียง 1 รายการ
- ยังขาด: ไม่มี

## เฟส 4: กันการจองซ้อนเมื่อยืนยันพร้อมกัน (AC-BKG-04)

### T-09 ทดสอบผู้ใช้ 2 คนยืนยันพร้อมกัน
- รองรับ: NFR-REL-03, CON-CONC-01
- ตรวจด้วย: AC-BKG-04
- ไฟล์ที่แตะ: `backend/tests/test_AC_BKG_04_concurrent_booking_prevented.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-07
- เสร็จเมื่อ: `test_AC_BKG_04_concurrent_booking_prevented` ผ่าน (ใช้ 2 thread ยิง POST /api/reservations พร้อมกัน ได้สำเร็จ 1 และไม่ว่าง 1)
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 4
- test ที่ต้องผ่านทั้งหมด: `test_AC_BKG_04_*` และ test ของเฟส 0 ถึง 3 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000`
- คนลองเองตาม AC-BKG-04:
  Given เปิดหลังบ้านใหม่ และเลือกพื้นที่กับช่วงเวลาที่ว่าง 1 ช่วง
  When เปิด terminal 2 หน้าต่าง สั่ง `curl -X POST` ไปที่ /api/reservations ด้วยข้อมูลเดียวกันเกือบพร้อมกัน
  Then ได้ผลสำเร็จ 1 รายการ อีกรายการได้ผลพื้นที่ไม่ว่าง
- ยังขาด: ไม่มี

## ตารางตรวจความครบ

### 1. AC กับ task
| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-BKG-01 | T-03, T-04 |
| AC-BKG-02 | T-05, T-06 |
| AC-BKG-03 | T-07, T-08 |
| AC-BKG-04 | T-09 |

### 2. Constraint กับ task
| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| CON-ELG-01 | T-05 |
| CON-CONC-01 | T-01, T-05, T-07, T-09 |

หมายเหตุ: Constraint ใน `specs/000-shared/constraints.md` (CON-TECH-01, DOM-PDPA-01, IF-IDP-01, IF-HIS-01, IF-NOT-01) ระบุผู้อ้างเป็น 001-booking เท่านั้น และ spec ของ 004 ไม่มีบรรทัด "ใช้ร่วม" จึงไม่นับเป็น Constraint ของฟีเจอร์นี้

### 3. FR กับ AC
| FR ID | AC ที่ตรวจ FR นี้ | เฟส |
|---|---|---|
| FR-BKG-01 | AC-BKG-01 | เฟส 0, 1 |
| FR-BKG-02 | AC-BKG-02, AC-BKG-03 | เฟส 2, 3 |
| FR-BKG-03 | AC-BKG-02 | เฟส 2 |
| FR-BKG-04 | AC-BKG-03 | เฟส 3 |

## สิ่งที่ยังไม่ทำ

Open Questions ใน spec: ไม่มี

ข้อเสนอคำถามให้ทีม (ยังไม่ใช่ Q-xx ทีมต้องตัดสินว่าจะเพิ่มใน spec หรือไม่)
1. CON-ELG-01 ต้องรู้ว่าผู้จองเป็นใคร แต่ระบบยังไม่มีการยืนยันตัวตน (อยู่ใน 001/002 ที่ยังไม่มีใครทำ) เฟส 2 จะรับ user_id จากหน้าจออย่างไร และรายชื่อผู้มีสิทธิ์ตัวอย่างใช้อะไร (T-05 รอคำตอบนี้)
2. ASM-02 (จองล่วงหน้าไม่เกิน 1 วัน สูงสุด 1 รายการต่อวัน) ไม่มี FR หรือ AC รองรับ จึงไม่มี task ทีมต้องการเพิ่ม FR หรือไม่
3. ASM-03 (ยกเลิกเมื่อไม่สแกนยืนยัน) และ ASM-04 (ยกเลิกการจองได้) ไม่มี FR หรือ AC รองรับ จึงไม่มี task
