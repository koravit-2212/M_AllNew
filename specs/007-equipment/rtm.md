# RTM: ใช้บริการยืมอุปกรณ์ (Equipment Loan)
อ้างอิง: spec.md SPEC-EQP-001 Draft v3 | tasks.md (T-01 ถึง T-15 เสร็จ) | test-cases.md (19 แถว ใช้ได้)
สร้างด้วย /verify เมื่อ 2569-11-12 | test: 71 ผ่าน 0 ไม่ผ่าน (pytest 43, vitest 28)

หมายเหตุ: spec.md ของ 007 ไม่มีบรรทัด "ใช้ร่วม" จึงไม่มี Constraint จาก `specs/000-shared/constraints.md` ที่นับเป็นของฟีเจอร์นี้ (ไฟล์ร่วมระบุผู้อ้างเป็น 001-booking เท่านั้น) และ spec ไม่มีหมวด "หน้าจอ (UI)" จึงไม่มีข้อความที่ "ต้องตรง" กับ mockup

## 1. ตามรอยไปข้างหน้า (requirement ไป โค้ด ไป test)
| ID | AC | task | โค้ด (ไฟล์: ฟังก์ชัน) | test (ผล) | สถานะ |
|---|---|---|---|---|---|
| FR-EQP-01 | AC-EQP-01 | T-01, T-02, T-03, T-04 | `api/equipment.py: list_equipment_types`, `pages/EquipmentLoanPage.jsx` (รายการและการเลือก), `App.jsx` (เมนู) | test_TC_EQP_01_1 (pytest+vitest ผ่าน), test_TC_EQP_01_2 (ผ่าน), test_TC_EQP_01_3 (ผ่าน), test_AC_EQP_01_show_equipment_types (ผ่าน) | ครบ |
| FR-EQP-02 | AC-EQP-02, AC-EQP-03 | T-03, T-05, T-09 | `services/equipment_service.py: create_loan_request` (ตรวจคงเหลือก่อนสร้างคำขอ), `approve_request` (ตรวจซ้ำใต้ lock), `EquipmentLoanPage.jsx: selectedOutOfStock` | test_TC_EQP_02_2, 02_3, 03_1, 03_2, 03_3 (ผ่าน) | ช่องโหว่ (F-04) |
| FR-EQP-03 | AC-EQP-02, AC-EQP-04 | T-06, T-08, T-11 | `equipment_service.py: get_request_detail, list_pending_requests`, `api/equipment.py: GET /api/loan-requests, GET /api/loan-requests/{id}`, `pages/StaffLoanApprovalPage.jsx` (การ์ดข้อมูลคำขอ) | test_TC_EQP_02_2 (pytest+vitest ผ่าน), test_TC_EQP_04_1 (ผ่าน), test_TC_EQP_04_4 (ผ่าน) | ช่องโหว่ (F-03) |
| FR-EQP-04 | AC-EQP-02 | T-06, T-08, T-13 | `equipment_service.py: approve_request, compute_due_date, library_today`, `config.py: EQUIPMENT_LOAN_DAYS, LIBRARY_TIMEZONE`, `StaffLoanApprovalPage.jsx: approve, formatDueDate` | test_TC_EQP_02_1 (pytest+vitest ผ่าน), test_TC_EQP_02_4 (ผ่าน), test_TC_EQP_04_2 (ผ่าน) | ช่องโหว่ (F-05) |
| FR-EQP-05 | AC-EQP-03 | T-09, T-10, T-15 | `api/equipment.py: create_loan_request_endpoint` (409 "ไม่สามารถยืมได้"), `EquipmentLoanPage.jsx` (ป้าย "หมด", ข้อความ, ปิดปุ่ม, `submitRejected`) | test_TC_EQP_03_1 (pytest+vitest ผ่าน), 03_2, 03_3, 03_4 (ผ่าน), test_TC_EQP_04_5 (ผ่าน) | ช่องโหว่ (F-02) |
| FR-EQP-06 | AC-EQP-04 | T-11, T-12, T-14 | `equipment_service.py: approve_request` (StudentBlocked), `api/equipment.py: POST .../approve, POST .../override`, `StaffLoanApprovalPage.jsx` (คำเตือน ปุ่ม override) | test_TC_EQP_02_5, 04_1, 04_2, 04_3, 04_4, 04_5 (ผ่าน) | ครบ |
| NFR-USB-01 | ไม่มี AC | T-02, T-04, T-07, T-08, T-10, T-12 | `frontend/index.html` (meta viewport), Tailwind class `md:` ในหน้า 007 | ไม่มี test อัตโนมัติ และไม่มีแถว "คน" ใน test-cases.md | ช่องโหว่ (F-06) |
| CON-LNS-02 | ไม่มี AC | T-01, T-06, T-11, T-13 | `equipment_service.py: compute_due_date` (กำหนดคืน), `config.py: EQUIPMENT_STUDENT_SEED_DATA` (รายการค้างคืนตัวอย่าง) | test_TC_EQP_02_1, 02_4 (due date ผ่าน) ไม่มี test ว่าการยืมที่เกินกำหนดกลายเป็นรายการค้างคืน | ช่องโหว่ (F-01) |

## 2. ตามรอยย้อนกลับ (โค้ด ไป requirement)
| โค้ด (ไฟล์: ฟังก์ชัน หรือ endpoint) | อ้าง ID | ตรงกับข้อความใน spec ไหม | หมายเหตุ |
|---|---|---|---|
| `GET /api/equipment-types` (`list_equipment_types`) | FR-EQP-01, FR-EQP-02 | ตรง | มีใน plan ข้อ 4 คืนทุกประเภทรวมคงเหลือ 0 ตาม Q-06 |
| `GET /api/students` (`list_students`) | FR-EQP-03 | ตรงบางส่วน | ไม่มีใน plan ข้อ 4 แต่มี Q-05 รองรับ (ชั่วคราว) FR-EQP-03 พูดถึงเจ้าหน้าที่ตรวจข้อมูล ไม่ใช่การเลือกนักศึกษา การอ้าง ID จึงไม่ตรงเรื่องนัก ควรอ้าง Q-05 |
| `POST /api/loan-requests` (`create_loan_request_endpoint`) | FR-EQP-02, FR-EQP-05, ASM-01 | ตรง | มีใน plan ข้อ 4 |
| `GET /api/loan-requests` (`list_pending_requests_endpoint`) | FR-EQP-03 | ตรงเรื่อง แต่ไม่มีใน plan ข้อ 4 | plan มีแค่หน้าจอ "Pending requests list" ไม่มี API (F-03) |
| `GET /api/loan-requests/{id}` (`get_loan_request_endpoint`) | FR-EQP-03, FR-EQP-06, CON-LNS-02 | ตรง | ส่ง `due_date` ล่วงหน้า (ถ้าอนุมัติวันนี้) ด้วย |
| `POST /api/loan-requests/{id}/approve` | FR-EQP-03, FR-EQP-04, ASM-02 | ตรง | plan ข้อ 4 ให้รับ `action(approve/decline)` และ `override=true` ในตัวเดียว โค้ดแยก override เป็น endpoint ของตัวเอง ไม่มี decline (spec ไม่มี FR ปฏิเสธ) |
| `POST /api/loan-requests/{id}/override` | FR-EQP-06, ASM-02, Q-04 | ตรง | มีใน plan ข้อ 4 ไม่มี audit log / override_by ตาม plan ข้อ 3 เพราะ Q-04 ไม่บังคับเหตุผล และยังไม่มีล็อกอิน (Q-05) |
| `POST /api/loan-requests/{id}/return` (plan ข้อ 4) | - | ไม่ได้สร้าง | ไม่มี FR การคืนอุปกรณ์ใน spec (เกี่ยวกับ F-01) |
| `equipment_service.py: compute_due_date` + `config.py: EQUIPMENT_LOAN_DAYS` | FR-EQP-04, ASM-03, Q-03 | ตรง | 1 วันทุกประเภทตาม Q-03 อยู่ใน config |
| `config.py: LIBRARY_TIMEZONE = 'Asia/Bangkok'` | FR-EQP-04 อ้าง glossary | spec 007 ไม่ได้บอก | glossary ที่อ้างเป็นของโดเมนตรวจสุขภาพ (F-05) |
| `config.py: EQUIPMENT_SEED_DATA`, `EQUIPMENT_STUDENT_SEED_DATA` | FR-EQP-01..03 | ข้อมูลตัวอย่าง (ทีมเลือกเอง) | รายการค้างคืนมาจาก seed ไม่ได้มาจากการยืมจริง (F-01) |
| `EquipmentLoanPage.jsx: REQUEST_QUANTITY = 1` | (ทีมเลือกเอง) | spec ไม่ได้บอก | ตัวเลขฝังในหน้า ไม่ได้อยู่ใน config (F-04) |
| `EquipmentLoanPage.jsx` ช่องเลือก "นักศึกษา" | Q-05 | ตรงตามคำตอบ Q-05 | ไม่มีใน mockup ชั่วคราว |
| `EquipmentLoanPage.jsx: submitRejected` | FR-EQP-05 (T-15) | ตรงบางส่วน | แสดง "ไม่สามารถยืมได้" กับทุกความล้มเหลว (F-02) |
| `StaffLoanApprovalPage.jsx` รายการคำขอที่รอตรวจด้านบน | FR-EQP-03 | ตรงเรื่อง | ไม่มีใน mockup UI-EQP-02 อ้าง plan "Pending requests list" (F-03) |
| `StaffLoanApprovalPage.jsx` คำเตือน ปุ่ม override กำหนดคืน | FR-EQP-04, FR-EQP-06, ASM-02 | ตรง | ข้อความตาม UI-EQP-02 |
| `App.jsx` เมนู "อนุมัติยืมอุปกรณ์ (เจ้าหน้าที่)" | FR-EQP-03, FR-EQP-04, Q-05 | ตรง | ไม่ตรวจสิทธิ์ตาม Q-05 (ชั่วคราว) |

## 3. ข้อค้นพบ
ชนิด: AC ไม่มี test / test อ่อน / โค้ดไม่มี FR / FR ไม่มี AC / เดา Q-xx / ละเมิด Constraint / ตัวเลขไม่ตรง spec / อ้าง ID ผิดเรื่อง
ทีมตัดสิน: แก้โค้ด / แก้ spec / เพิ่ม Q-xx / ไม่ใช่ปัญหา (พร้อมเหตุผล 1 บรรทัด)

| F-ID | ชนิด | อยู่ที่ | ขัดกับ | รายละเอียด | ทีมตัดสิน |
|---|---|---|---|---|---|
| F-01 | FR ไม่มี AC | `backend/app/config.py: EQUIPMENT_STUDENT_SEED_DATA`, `models/equipment.py: Student.outstanding_items` | CON-LNS-02, FR-EQP-06, AC-EQP-04 | CON-LNS-02 (ต้องคืนภายในเวลาที่กำหนด) ไม่มี AC ระบบกำหนด due date ได้ แต่การยืมที่เกิน due date ไม่เคยกลายเป็น "รายการค้างคืน" เพราะ `outstanding_items` มาจากข้อมูลตัวอย่างใน config เท่านั้น และไม่มีการคืนอุปกรณ์ (plan มี `/return` แต่ spec ไม่มี FR) รายการค้างคืนหนังสือตาม AC-EQP-04 ก็ยังไม่เชื่อมกับ 005 ผลคือในระบบจริง ไม่มีใครถูกบล็อกตาม ASM-02 เลย ควรเพิ่ม Q-xx ว่ารายการค้างคืนมาจากไหน และจะมี FR การคืนหรือไม่ | |
| F-02 | อ้าง ID ผิดเรื่อง | `frontend/src/pages/EquipmentLoanPage.jsx: submitRequest` (catch ที่ตั้ง `submitRejected`) | FR-EQP-05 | FR-EQP-05 ให้แจ้ง "ไม่สามารถยืมได้" เมื่ออุปกรณ์หมด แต่โค้ดแสดงข้อความนี้กับทุกความล้มเหลว เช่น เน็ตหลุด หลังบ้านล่ม หรือไม่พบรหัสนักศึกษา (404) ผู้ใช้จะเข้าใจว่าของหมดทั้งที่ไม่ใช่ วิธีแก้ที่เป็นไปได้: ให้ `client.js` ส่ง status ใน error แล้วแสดงเฉพาะ 409 ส่วนข้อความกรณีอื่นต้องถามทีม (spec ไม่ได้บอก) | |
| F-03 | โค้ดไม่มี FR | `backend/app/api/equipment.py: GET /api/loan-requests`, `StaffLoanApprovalPage.jsx` รายการคำขอด้านบน | plan.md ข้อ 4, UI-EQP-02 | API รายการคำขอที่รอตรวจและรายการบนหน้าเจ้าหน้าที่ ไม่มีในรายการ API ของ plan ข้อ 4 และไม่มีใน mockup UI-EQP-02 อ้างแค่หน้าจอ "Pending requests list" ในข้อความ plan ข้อ 4 จำเป็นต่อการใช้งาน (เจ้าหน้าที่ต้องเลือกคำขอ) แต่ทีมควรยืนยันและเพิ่มใน plan / mockup | |
| F-04 | ตัวเลขไม่ตรง spec | `frontend/src/pages/EquipmentLoanPage.jsx: REQUEST_QUANTITY = 1` | FR-EQP-02, plan.md ข้อ 4 (input quantity) | spec ไม่ได้กำหนดจำนวนต่อคำขอ plan ให้ API รับ `quantity` แต่หน้าจอล็อกไว้ที่ 1 ชิ้นเพราะ mockup แสดง "× 1" เป็นการตัดสินใจแทนทีม และตัวเลขฝังในหน้า ไม่ได้อยู่ใน `frontend/src/config.js` ควรถามทีมว่าขอได้ครั้งละกี่ชิ้น | |
| F-05 | เดา Q-xx | `backend/app/config.py: LIBRARY_TIMEZONE` | FR-EQP-04, `specs/000-shared/glossary.md` | การนับ "วันที่ยืม" ใช้ Asia/Bangkok โดยอ้าง glossary "วันเดียวกัน" แต่ glossary ร่วมเป็นของโดเมนตรวจสุขภาพ (ผู้รับบริการ HN) ไม่ใช่ห้องสมุด spec 007 ไม่ได้บอกเขตเวลา ค่าน่าจะถูกแต่ทีมควรยืนยัน และควรแก้ไฟล์ใน 000-shared ให้เป็นของโปรเจกต์ห้องสมุด | |
| F-06 | FR ไม่มี AC | `frontend/` ทั้งหมด | NFR-USB-01 | NFR-USB-01 (ใช้ได้บนคอมพิวเตอร์และมือถือ) ไม่มี AC และไม่มีแถว test-cases ทั้งแบบอัตโนมัติและแบบ "คน" มีแค่ meta viewport และ class `md:` จึงยังไม่มีหลักฐานว่าใช้งานบนมือถือได้ ควรเพิ่ม AC หรือแถว "คน" ให้ลองบนมือถือ | |

## 4. แก้แล้ว
| F-ID | แก้อย่างไร | รู้ได้อย่างไร |
|---|---|---|
| (ยังไม่มี rtm.md ก่อนหน้า) | - | - |
