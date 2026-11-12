# RTM: จอง/ใช้พื้นที่ในห้องสมุด (Space Booking)
อ้างอิง: spec.md SPEC-BKG-002 Draft v3 (Q-01 ถึง Q-08) | tasks.md (T-01 ถึง T-09 เสร็จ รอทีมตรวจ) | test-cases.md (13 แถวใช้ได้ + TC-BKG-NFR-1 ร่าง)
สร้างด้วย /verify เมื่อ 2569-11-12 | test: 50 ผ่าน 0 ไม่ผ่าน (pytest 32, vitest 18)

หมายเหตุ: spec 004 ไม่มีบรรทัด "ใช้ร่วม" จึงไม่มี Constraint จาก `specs/000-shared/constraints.md` (ไฟล์ร่วมเป็นของ 001-booking) และไม่มีหมวด "หน้าจอ (UI)" จึงไม่มีข้อความที่ "ต้องตรง" กับ mockup
ช่อง "ทีมตัดสิน" ด้านล่าง AI เขียนแทนตามคำสั่งทีม "ตัดสินใจเองทั้งหมดได้เลย" (2569-11-12) ทีมควรตรวจ

## 1. ตามรอยไปข้างหน้า (requirement ไป โค้ด ไป test)
| ID | AC | task | โค้ด (ไฟล์: ฟังก์ชัน) | test (ผล) | สถานะ |
|---|---|---|---|---|---|
| FR-BKG-01 | AC-BKG-01 | T-01, T-02, T-03, T-04 | `api/spaces.py: list_available_spaces`, `models/space.py: build_seed_space_store`, `pages/SpaceBookingPage.jsx` (รายการพื้นที่และช่วงเวลา), `App.jsx` (เมนู) | test_TC_BKG_01_1, 01_2 (pytest+vitest ผ่าน), 01_3 (ผ่าน), test_AC_BKG_01_* (ผ่าน) | ช่องโหว่ (F-05) |
| FR-BKG-02 | AC-BKG-02, AC-BKG-03 | T-05, T-07 | `services/reservation_service.py: check_availability, create_reservation, _slot_taken` | test_TC_BKG_02_1, 03_1, 03_2, 03_3 (ผ่าน) | ช่องโหว่ (F-03) |
| FR-BKG-03 | AC-BKG-02 | T-05, T-06 | `api/reservations.py: create_reservation_endpoint, get_reservation_endpoint`, `SpaceBookingPage.jsx` (ขั้นยืนยันและผลการจอง) | test_TC_BKG_02_1 (pytest+vitest ผ่าน), 02_2 (ผ่าน) | ครบ |
| FR-BKG-04 | AC-BKG-03 | T-07, T-08 | `create_reservation` (SlotUnavailable), `api/reservations.py` (409 "พื้นที่ไม่ว่างในช่วงเวลานี้"), `SpaceBookingPage.jsx` (สถานะไม่ว่าง) | test_TC_BKG_03_1 (pytest+vitest ผ่าน), 03_2 (ผ่าน) | ครบ |
| NFR-USB-01 | ไม่มี AC | T-02, T-04, T-06, T-08 | `frontend/index.html` (meta viewport), Tailwind `md:` | ไม่มี test อัตโนมัติ TC-BKG-NFR-1 (คน) ยังเป็นร่าง | ช่องโหว่ (F-01) |
| NFR-REL-03 | AC-BKG-04 | T-09 | `create_reservation` (`with store.lock` ครอบตรวจและบันทึก) | test_TC_BKG_04_1, 04_2, 04_3 (ผ่าน), test_AC_BKG_04_* (ผ่าน) ตรวจแล้วว่าเอา lock ออก test ไม่ผ่าน | ครบ |
| CON-ELG-01 | ไม่มี AC ตรง (ตรวจใน TC-BKG-02-3) | T-05 | `reservation_service.py: is_eligible, find_user`, `config.py: SPACE_ELIGIBLE_USER_TYPES` | test_TC_BKG_02_3 (pytest+vitest ผ่าน), test_AC_BKG_02_not_eligible_user_rejected (ผ่าน) | ครบ |
| CON-CONC-01 | AC-BKG-04 | T-01, T-05, T-07, T-09 | `models/space.py: SpaceStore.lock`, `create_reservation` | test_TC_BKG_04_* (ผ่าน) | ครบ |

## 2. ตามรอยย้อนกลับ (โค้ด ไป requirement)
| โค้ด (ไฟล์: ฟังก์ชัน หรือ endpoint) | อ้าง ID | ตรงกับข้อความใน spec ไหม | หมายเหตุ |
|---|---|---|---|
| `GET /api/spaces/available` | FR-BKG-01, FR-BKG-02 | ตรง | ไม่แสดงพื้นที่ที่ปิด มีใน plan ข้อ 4 รูปแบบ output ต่างจาก plan เล็กน้อย (บันทึกใน plan แล้ว) |
| `POST /api/reservations/check-availability` | FR-BKG-02 | ตรง | มีใน plan หน้าจอไม่ได้เรียก (หลังบ้านตรวจอีกครั้งตอนบันทึกอยู่แล้ว) |
| `POST /api/reservations` | FR-BKG-02, FR-BKG-03, FR-BKG-04, CON-ELG-01, CON-CONC-01 | ตรง | 403 / 409 / 404 |
| `GET /api/reservations/{id}` | FR-BKG-03 | ตรง | มีใน plan |
| `GET /api/space-users` | CON-ELG-01, Q-01 | ตรงตาม Q-01 | เพิ่มใน plan แล้ว (แก้ F-06) |
| `config.py: SPACE_ELIGIBLE_USER_TYPES` | CON-ELG-01, Q-01 | ตรง | |
| `config.py: SPACE_BOOKING_TIMEZONE` | Q-05 | ตรง | เดิมอ้าง glossary ของโดเมนอื่น (แก้ F-04) |
| `config.py: SPACE_SEED_DATA` (capacity = 1) | ASM-01, Q-06 | ตรงตาม Q-06 | โค้ดไม่ใช้ capacity |
| `models/space.py: build_seed_space_store` (สร้างช่วงเวลาของวันเปิดหลังบ้าน) | FR-BKG-01 | ตรงบางส่วน | ข้ามวันแล้วช่วงเวลายังเป็นของวันเก่า (F-05, Q-08) |
| `SpaceBookingPage.jsx` ช่องเลือก "ผู้จอง" | Q-01 | ตรงตาม Q-01 | ไม่มีใน mockup ชั่วคราว |
| `SpaceBookingPage.jsx` ขั้น "ยืนยัน" (การ์ด + "ยืนยันการจอง" + "กลับ") | FR-BKG-02, FR-BKG-03 | ตรง | mockup มีแถบขั้น "2 ยืนยัน" แต่ไม่มีหน้าจอสถานะนี้ ใช้การ์ดเดียวกับผลการจอง |
| `SpaceBookingPage.jsx` ข้อความ "ไม่มีสิทธิ์จองพื้นที่", "จองไม่สำเร็จ กรุณาลองใหม่" | Q-01, Q-04 | ตรง | |
| ASM-02, ASM-03, ASM-04 | Q-02, Q-03 | ไม่ได้สร้าง | ไม่มี FR / AC รองรับ ตาม Q-02, Q-03 |

## 3. ข้อค้นพบ
ชนิด: AC ไม่มี test / test อ่อน / โค้ดไม่มี FR / FR ไม่มี AC / เดา Q-xx / ละเมิด Constraint / ตัวเลขไม่ตรง spec / อ้าง ID ผิดเรื่อง
ทีมตัดสิน: แก้โค้ด / แก้ spec / เพิ่ม Q-xx / ไม่ใช่ปัญหา (พร้อมเหตุผล 1 บรรทัด)

| F-ID | ชนิด | อยู่ที่ | ขัดกับ | รายละเอียด | ทีมตัดสิน |
|---|---|---|---|---|---|
| F-05 | เดา Q-xx | `backend/app/api/spaces.py: _store = build_seed_space_store()`, `models/space.py: build_seed_space_store` | FR-BKG-01 | ช่วงเวลาถูกสร้างครั้งเดียวตอนเปิดหลังบ้าน เป็นของ "วันนั้น" ถ้าเปิดหลังบ้านค้างข้ามวัน หน้าจอจะยังให้จองช่วงเวลาของเมื่อวาน spec ไม่ได้บอกว่าช่วงเวลาของแต่ละวันมาจากไหน | เพิ่ม Q-xx: Q-08 (เปิด) รอทีมตอบ ระหว่างนี้รีสตาร์ตหลังบ้านทุกวัน |
| F-03 | เดา Q-xx | `backend/app/api/spaces.py: slot_is_available`, `services/reservation_service.py: create_reservation` | FR-BKG-02 | ความว่างดูแค่ว่ามีคนจองหรือยัง ไม่ดูเวลาปัจจุบัน เช่น 16.00 น. ยังจองช่วง 09.00–11.00 น. ของวันนี้ได้ spec ไม่ได้บอกว่าช่วงที่เลยมาแล้วนับเป็น "ว่าง" หรือไม่ | เพิ่ม Q-xx: Q-07 (เปิด) รอทีมตอบ |
| F-01 | FR ไม่มี AC | `frontend/` ทั้งหมด | NFR-USB-01 | NFR-USB-01 ไม่มี AC และยังไม่มีผลการลองบนมือถือ เพิ่มแถว "คน" TC-BKG-NFR-1 แล้วแต่ยังเป็นร่าง | แก้ spec: เพิ่มแถว TC-BKG-NFR-1 รอทีมตรวจแถวและลองบนมือถือ |

## 4. แก้แล้ว
| F-ID | แก้อย่างไร | รู้ได้อย่างไร |
|---|---|---|
| F-02 | (ตัวเลขไม่ตรง spec: `Space.capacity` มีในข้อมูลแต่โค้ดจองได้ 1 รายการต่อช่วงเสมอ) เพิ่ม Q-06 ใน spec: 1 พื้นที่ 1 ช่วง จองได้ 1 รายการ capacity เป็นข้อมูลประกอบ | เปิด spec Q-06 เทียบกับ `create_reservation` |
| F-04 | (เดา Q-xx: เขตเวลาอ้าง glossary ของโดเมนตรวจสุขภาพ) เพิ่ม Q-05 Asia/Bangkok และแก้คอมเมนต์ใน `config.py` ให้อ้าง Q-05 | เปิด spec Q-05 และ `config.py: SPACE_BOOKING_TIMEZONE` |
| F-06 | (โค้ดไม่มี FR: `GET /api/space-users` ไม่มีใน plan) เพิ่มใน plan ข้อ 4 พร้อมตาราง "ค่าที่ตั้งได้" | เปิด plan ข้อ 4 เทียบกับ `api/reservations.py` |
