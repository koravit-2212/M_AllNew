# tasks: ใช้บริการยืมอุปกรณ์ (Equipment Loan)

- Feature: ใช้บริการยืมอุปกรณ์
- Spec ID: SPEC-EQP-001 (`specs/007-equipment/spec.md` Draft v2)
- อ้างอิง: `specs/007-equipment/plan.md`
- วันที่: 2569-11-12

สรุป
1. มี 6 เฟส (เฟส 0 ถึงเฟส 4 และเฟสรอคำตอบ) รวม 14 task
2. task ที่ต้องรอคำตอบ: 2 task (T-13, T-14) spec ไม่มี Q-xx ค้าง แต่ 2 เรื่องนี้ spec ยังไม่ชัดพอให้ทำโดยไม่เดา ดู "ข้อเสนอคำถาม" ข้อ 1 และ 2 ทีมต้องเพิ่มเป็น Q-xx ใน spec และตอบก่อน
3. เฟสแรกที่ลองใช้งานได้จริงคือเฟส 1 (นักศึกษาเห็นประเภทอุปกรณ์ที่ยืมได้) ส่วนเฟส 0 ลองได้แค่เมนูสลับหน้า

หมายเหตุทางเทคนิค (ทีมเลือกเอง ไม่ได้มาจาก spec)
- plan.md เลือก PostgreSQL แต่โค้ดที่มีอยู่ของ 003 ใช้ข้อมูลในหน่วยความจำ task ชุดนี้ทำตามแนวทางเดียวกับ 003 คือเก็บอุปกรณ์ นักศึกษา คำขอ และการยืมในหน่วยความจำ
- รายการค้างคืนของนักศึกษาควรมาจาก 005-borrow-return ซึ่งยังไม่มีใครทำ จึงใช้ข้อมูลตัวอย่างใน `config.py` ไปก่อน
- plan.md ข้อ 4 มี API คืนอุปกรณ์ (return) และหน้า Admin Inventory แต่ spec ไม่มี FR เรื่องการคืนอุปกรณ์ และการจัดการอุปกรณ์อยู่ใน Out of scope จึงไม่สร้าง task
- spec.md ไม่มีหมวด "หน้าจอ (UI)" จึงยังไม่มีข้อความที่ระบุว่า "ต้องตรง" กับ mockup task หน้าจอใช้ข้อความจาก `mockups/UI-EQP-01-student-request.html` และ `mockups/UI-EQP-02-staff-approve.html` เป็นแนวทาง และทีมควรตรวจด้วยตา

## เฟส 0: ฐานราก (ไม่มี AC เป็นงานพื้นฐาน)

### T-01 สร้างข้อมูลอุปกรณ์และนักศึกษาตัวอย่าง พร้อมที่เก็บคำขอยืมและการยืม
- รองรับ: FR-EQP-01, FR-EQP-02 (จำนวนคงเหลือ), FR-EQP-03 (รายการค้างคืนของนักศึกษา), CON-LNS-02
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-03, T-05, T-06, T-09, T-11
- ไฟล์ที่แตะ: `backend/app/config.py`, `backend/app/models/equipment.py`, `backend/tests/test_EQP_T01_equipment_store.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: `test_EQP_T01_equipment_store.py` ผ่าน โดยยืนยันว่ามีอุปกรณ์ 3 ประเภท (ปลั๊กไฟ ร่ม ถุงผ้า) พร้อมจำนวนคงเหลือ มีนักศึกษาตัวอย่างทั้งแบบไม่มีและมีรายการค้างคืน และที่เก็บคำขอยืมเริ่มต้นว่าง
- สถานะ: เสร็จ

### T-02 เพิ่มเมนูไปหน้ายืมอุปกรณ์ใน App.jsx โดยไม่ลบหน้าเดิม
- รองรับ: FR-EQP-01 (จุดเข้าหน้ายืมอุปกรณ์), NFR-USB-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-04
- ไฟล์ที่แตะ: `frontend/src/App.jsx`, `frontend/src/pages/EquipmentLoanPage.jsx`, `frontend/src/__tests__/App.test.jsx`
- แบบหน้าจอ: UI-EQP-01 `mockups/UI-EQP-01-student-request.html` (เฉพาะแถบชื่อหน้า "ยืมอุปกรณ์")
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: `App.test.jsx` ผ่าน กดเมนู "ยืมอุปกรณ์" แล้วเห็นหัวข้อ "ยืมอุปกรณ์" และกดกลับเมนู "หนังสือ" แล้วเห็นหน้าค้นหาเดิม
- สถานะ: เสร็จ

#### จุดตรวจเฟส 0
- test ที่ต้องผ่านทั้งหมด: `test_EQP_T01_equipment_store.py`, `App.test.jsx` และ test เดิมของ 003 ทั้งหมดต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเอง (ไม่มี AC):
  Given เปิดเว็บที่ port 5173
  When กดเมนู "ยืมอุปกรณ์" แล้วกดเมนู "หนังสือ"
  Then เห็นหัวข้อ "ยืมอุปกรณ์" และกลับมาเห็นหน้าค้นหาหนังสือเดิมได้
- ยังขาด: ไม่มี

## เฟส 1: นักศึกษาเห็นประเภทอุปกรณ์ที่ยืมได้ (AC-EQP-01)

### T-03 สร้าง API GET /api/equipment-types และลงทะเบียน router
- รองรับ: FR-EQP-01, FR-EQP-02
- ตรวจด้วย: AC-EQP-01
- ไฟล์ที่แตะ: `backend/app/api/equipment.py`, `backend/app/main.py`, `backend/tests/test_AC_EQP_01_equipment_types.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: `test_AC_EQP_01_show_equipment_types` ผ่าน (API คืนประเภทอุปกรณ์ทั้ง 3 พร้อมจำนวนคงเหลือ)
- สถานะ: เสร็จ รอทีมตรวจ

### T-04 แสดงรายการอุปกรณ์ให้นักศึกษาเลือก
- รองรับ: FR-EQP-01, NFR-USB-01
- ตรวจด้วย: AC-EQP-01
- ไฟล์ที่แตะ: `frontend/src/api/client.js`, `frontend/src/pages/EquipmentLoanPage.jsx`, `frontend/src/__tests__/EquipmentLoanPage.test.jsx`
- แบบหน้าจอ: UI-EQP-01 `mockups/UI-EQP-01-student-request.html` (สถานะปกติ AC-EQP-01)
- ต้องทำหลัง: T-02, T-03
- เสร็จเมื่อ: test หน้าจอ AC-EQP-01 ผ่าน (ใช้ client จำลอง เห็นชื่ออุปกรณ์ จำนวนคงเหลือ และป้าย "ว่าง")
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 1
- test ที่ต้องผ่านทั้งหมด: `test_AC_EQP_01_*` (หลังบ้าน), `EquipmentLoanPage.test.jsx` (AC-EQP-01) และ test ของเฟส 0 กับ 003 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-EQP-01:
  Given ใช้ข้อมูลอุปกรณ์ตัวอย่างจาก `config.py`
  When กดเมนู "ยืมอุปกรณ์"
  Then เห็นปลั๊กไฟ ร่ม และถุงผ้า พร้อมจำนวนคงเหลือให้เลือก
- ยังขาด: ไม่มี

## เฟส 2: เจ้าหน้าที่อนุมัติ ระบบบันทึกการยืมและลดจำนวนคงเหลือ (AC-EQP-02)

### T-05 สร้าง API ส่งคำขอยืม (สถานะรออนุมัติ)
- รองรับ: FR-EQP-02, ASM-01 (ต้องผ่านเจ้าหน้าที่เสมอ)
- ตรวจด้วย: AC-EQP-02
- ไฟล์ที่แตะ: `backend/app/services/equipment_service.py`, `backend/app/api/equipment.py`, `backend/tests/test_AC_EQP_02_create_request.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: test ที่ชื่อมี `AC_EQP_02` ผ่าน (POST /api/loan-requests เมื่ออุปกรณ์มีพอ ได้คำขอสถานะ pending และจำนวนคงเหลือยังไม่ลด)
- สถานะ: พร้อมทำ (ทีมควรตอบข้อเสนอคำถาม ข้อ 3 ก่อนเริ่ม)

### T-06 สร้าง API ให้เจ้าหน้าที่ดูคำขอและอนุมัติ แล้วบันทึกการยืมและลดจำนวนคงเหลือ
- รองรับ: FR-EQP-03, FR-EQP-04 (ยกเว้นการกำหนด due date ซึ่งอยู่ใน T-13), CON-LNS-02
- ตรวจด้วย: AC-EQP-02
- ไฟล์ที่แตะ: `backend/app/services/equipment_service.py`, `backend/app/api/equipment.py`, `backend/tests/test_AC_EQP_02_approve_and_record.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-05
- เสร็จเมื่อ: `test_AC_EQP_02_approve_and_record` ผ่าน (GET /api/loan-requests/{id} แสดงข้อมูลนักศึกษาและรายการค้างคืน "ไม่มี", POST /api/loan-requests/{id}/approve สร้างการยืมและจำนวนคงเหลือลดลงตามจำนวนที่ยืม)
- สถานะ: พร้อมทำ

### T-07 ทำปุ่ม "ส่งคำขอยืม" และหน้าผล "ส่งคำขอแล้ว" ของนักศึกษา
- รองรับ: FR-EQP-02, ASM-01, NFR-USB-01
- ตรวจด้วย: AC-EQP-02
- ไฟล์ที่แตะ: `frontend/src/api/client.js`, `frontend/src/pages/EquipmentLoanPage.jsx`, `frontend/src/__tests__/EquipmentLoanPage.test.jsx`
- แบบหน้าจอ: UI-EQP-01 `mockups/UI-EQP-01-student-request.html` (สถานะส่งคำขอแล้ว รอเจ้าหน้าที่)
- ต้องทำหลัง: T-04, T-05
- เสร็จเมื่อ: test หน้าจอที่ชื่อมี AC-EQP-02 ผ่าน (เลือกปลั๊กไฟ กด "ส่งคำขอยืม" แล้วเห็น "ส่งคำขอแล้ว")
- สถานะ: พร้อมทำ

### T-08 ทำหน้าเจ้าหน้าที่ตรวจสอบและอนุมัติคำขอ พร้อมเมนูใน App.jsx
- รองรับ: FR-EQP-03, FR-EQP-04, NFR-USB-01
- ตรวจด้วย: AC-EQP-02
- ไฟล์ที่แตะ: `frontend/src/App.jsx`, `frontend/src/api/client.js`, `frontend/src/pages/StaffLoanApprovalPage.jsx`, `frontend/src/__tests__/StaffLoanApprovalPage.test.jsx`
- แบบหน้าจอ: UI-EQP-02 `mockups/UI-EQP-02-staff-approve.html` (สถานะปกติ และสถานะอนุมัติแล้ว ยกเว้นช่อง "กำหนดคืน (due date)" ซึ่งอยู่ใน T-13)
- ต้องทำหลัง: T-06, T-07
- เสร็จเมื่อ: test หน้าจอ AC-EQP-02 ผ่าน (เห็นนักศึกษา อุปกรณ์ รายการค้างคืน "ไม่มี" กด "อนุมัติการยืม" แล้วเห็น "บันทึกการยืมแล้ว" และจำนวนคงเหลือใหม่)
- สถานะ: พร้อมทำ (ทีมควรตอบข้อเสนอคำถาม ข้อ 3 ก่อนเริ่ม)

#### จุดตรวจเฟส 2
- test ที่ต้องผ่านทั้งหมด: `test_AC_EQP_02_*`, test หน้าจอ AC-EQP-02 ทั้งของนักศึกษาและเจ้าหน้าที่ และ test ของเฟส 0 ถึง 1 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-EQP-02:
  Given ปลั๊กไฟมีคงเหลือ และใช้นักศึกษาตัวอย่างที่ไม่มีรายการค้างคืน
  When ส่งคำขอยืมปลั๊กไฟ 1 ชิ้นจากหน้า "ยืมอุปกรณ์" แล้วไปเมนูเจ้าหน้าที่ กด "อนุมัติการยืม"
  Then เห็น "บันทึกการยืมแล้ว" และกลับไปหน้า "ยืมอุปกรณ์" เห็นปลั๊กไฟคงเหลือลดลง 1
- ยังขาด: การกำหนด due date ตามประเภทอุปกรณ์ (T-13 รอคำตอบ)

## เฟส 3: อุปกรณ์หมด (AC-EQP-03)

### T-09 ปฏิเสธคำขอยืมอุปกรณ์ที่หมด
- รองรับ: FR-EQP-02, FR-EQP-05
- ตรวจด้วย: AC-EQP-03
- ไฟล์ที่แตะ: `backend/app/services/equipment_service.py`, `backend/app/api/equipment.py`, `backend/tests/test_AC_EQP_03_out_of_stock_message.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-05
- เสร็จเมื่อ: `test_AC_EQP_03_out_of_stock_message` ผ่าน (ขอยืมอุปกรณ์ที่คงเหลือ 0 ได้ผลไม่สามารถยืมได้ และไม่มีคำขอใหม่ถูกสร้าง)
- สถานะ: พร้อมทำ

### T-10 แสดง "ไม่สามารถยืมได้" และปิดปุ่มส่งคำขอเมื่ออุปกรณ์หมด
- รองรับ: FR-EQP-05, NFR-USB-01
- ตรวจด้วย: AC-EQP-03
- ไฟล์ที่แตะ: `frontend/src/pages/EquipmentLoanPage.jsx`, `frontend/src/__tests__/EquipmentLoanPage.test.jsx`
- แบบหน้าจอ: UI-EQP-01 `mockups/UI-EQP-01-student-request.html` (สถานะอุปกรณ์หมด AC-EQP-03)
- ต้องทำหลัง: T-07, T-09
- เสร็จเมื่อ: test หน้าจอ AC-EQP-03 ผ่าน (เลือกอุปกรณ์ที่คงเหลือ 0 แล้วเห็นป้าย "หมด" ข้อความ "ไม่สามารถยืมได้" และปุ่ม "ส่งคำขอยืม" กดไม่ได้)
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 3
- test ที่ต้องผ่านทั้งหมด: `test_AC_EQP_03_*`, test หน้าจอ AC-EQP-03 และ test ของเฟส 0 ถึง 2 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-EQP-03:
  Given อุปกรณ์ตัวอย่างประเภทหนึ่งมีคงเหลือ 0 (ตั้งใน `config.py` หรือยืมจนหมด)
  When เลือกอุปกรณ์นั้นในหน้า "ยืมอุปกรณ์"
  Then เห็น "ไม่สามารถยืมได้" และกดส่งคำขอยืมไม่ได้
- ยังขาด: ไม่มี

## เฟส 4: นักศึกษามีรายการค้างคืน เจ้าหน้าที่ต้องตรวจก่อน (AC-EQP-04)

### T-11 ให้ API รายละเอียดคำขอแสดงรายการค้างคืนของนักศึกษา
- รองรับ: FR-EQP-03, FR-EQP-06, CON-LNS-02
- ตรวจด้วย: AC-EQP-04
- ไฟล์ที่แตะ: `backend/app/services/equipment_service.py`, `backend/app/api/equipment.py`, `backend/tests/test_AC_EQP_04_outstanding_shown.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-06
- เสร็จเมื่อ: test ที่ชื่อมี `AC_EQP_04` ผ่าน (คำขอของนักศึกษาที่มีรายการค้างคืน ไม่ถูกอนุมัติเอง และ GET /api/loan-requests/{id} คืนรายการค้างคืนให้เจ้าหน้าที่เห็น)
- สถานะ: พร้อมทำ

### T-12 แสดงคำเตือน "มีรายการค้างคืน" ในหน้าเจ้าหน้าที่
- รองรับ: FR-EQP-06, NFR-USB-01
- ตรวจด้วย: AC-EQP-04
- ไฟล์ที่แตะ: `frontend/src/pages/StaffLoanApprovalPage.jsx`, `frontend/src/__tests__/StaffLoanApprovalPage.test.jsx`
- แบบหน้าจอ: UI-EQP-02 `mockups/UI-EQP-02-staff-approve.html` (สถานะมีรายการค้างคืน AC-EQP-04 ยกเว้นปุ่ม override ซึ่งอยู่ใน T-14)
- ต้องทำหลัง: T-08, T-11
- เสร็จเมื่อ: test หน้าจอ AC-EQP-04 ผ่าน (เห็นคำเตือน "มีรายการค้างคืน" พร้อมรายการที่ค้าง)
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 4
- test ที่ต้องผ่านทั้งหมด: `test_AC_EQP_04_*`, test หน้าจอ AC-EQP-04 และ test ของเฟส 0 ถึง 3 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-EQP-04:
  Given ใช้นักศึกษาตัวอย่างที่มีรายการค้างคืนใน `config.py`
  When นักศึกษาคนนั้นส่งคำขอยืมร่ม แล้วเจ้าหน้าที่เปิดคำขอ
  Then เจ้าหน้าที่เห็นคำเตือน "มีรายการค้างคืน" พร้อมรายการที่ค้างก่อนตัดสินใจ
- ยังขาด: ระบบบล็อกการยืมและปุ่มปลดล็อก (override) ตาม ASM-02 (T-14 รอคำตอบ)

## เฟสรอคำตอบ

### T-13 กำหนด due date ตามประเภทอุปกรณ์เมื่ออนุมัติ
- รองรับ: FR-EQP-04 (ส่วน due date), CON-LNS-02, ASM-03
- ตรวจด้วย: AC-EQP-02
- ไฟล์ที่แตะ: `backend/app/config.py`, `backend/app/services/equipment_service.py`, `frontend/src/pages/StaffLoanApprovalPage.jsx`, `backend/tests/test_AC_EQP_02_due_date.py`
- แบบหน้าจอ: UI-EQP-02 `mockups/UI-EQP-02-staff-approve.html` (ช่อง "กำหนดคืน (due date)")
- ต้องทำหลัง: T-08
- เสร็จเมื่อ: test due date ของแต่ละประเภทอุปกรณ์ผ่าน ตามค่าที่ทีมตอบ
- สถานะ: รอคำตอบ (ข้อเสนอคำถาม ข้อ 1 ทีมต้องเพิ่มเป็น Q-xx ใน spec)

### T-14 บล็อกการยืมเมื่อมีรายการค้างคืน และให้เจ้าหน้าที่ปลดล็อก (override)
- รองรับ: FR-EQP-06, ASM-02
- ตรวจด้วย: AC-EQP-04
- ไฟล์ที่แตะ: `backend/app/services/equipment_service.py`, `backend/app/api/equipment.py`, `frontend/src/pages/StaffLoanApprovalPage.jsx`, `backend/tests/test_AC_EQP_04_block_and_override.py`
- แบบหน้าจอ: UI-EQP-02 `mockups/UI-EQP-02-staff-approve.html` (ปุ่ม "ปลดล็อก (override) เป็นกรณีพิเศษ")
- ต้องทำหลัง: T-12
- เสร็จเมื่อ: test บล็อกและ override ผ่าน ตามกติกาที่ทีมตอบ
- สถานะ: รอคำตอบ (ข้อเสนอคำถาม ข้อ 2 ทีมต้องเพิ่มเป็น Q-xx ใน spec)

## ตารางตรวจความครบ

### 1. AC กับ task
| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-EQP-01 | T-03, T-04 |
| AC-EQP-02 | T-05, T-06, T-07, T-08, T-13 |
| AC-EQP-03 | T-09, T-10 |
| AC-EQP-04 | T-11, T-12, T-14 |

### 2. Constraint กับ task
| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| CON-LNS-02 | T-01, T-06, T-11, T-13 |

หมายเหตุ: Constraint ใน `specs/000-shared/constraints.md` ระบุผู้อ้างเป็น 001-booking เท่านั้น และ spec ของ 007 ไม่มีบรรทัด "ใช้ร่วม" จึงไม่นับเป็น Constraint ของฟีเจอร์นี้

### 3. FR กับ AC
| FR ID | AC ที่ตรวจ FR นี้ | เฟส |
|---|---|---|
| FR-EQP-01 | AC-EQP-01 | เฟส 0, 1 |
| FR-EQP-02 | AC-EQP-02, AC-EQP-03 | เฟส 1, 2, 3 |
| FR-EQP-03 | AC-EQP-02, AC-EQP-04 | เฟส 2, 4 |
| FR-EQP-04 | AC-EQP-02 | เฟส 2, รอคำตอบ (due date) |
| FR-EQP-05 | AC-EQP-03 | เฟส 3 |
| FR-EQP-06 | AC-EQP-04 | เฟส 4, รอคำตอบ (บล็อกและ override) |

## สิ่งที่ยังไม่ทำ

Open Questions ใน spec: ไม่มี (Q-01 และ Q-02 ตอบแล้วเป็น ASM-02 และ ASM-03)

ข้อเสนอคำถามให้ทีม (ยังไม่ใช่ Q-xx ทีมต้องเพิ่มใน spec และตอบ)
1. ASM-03 บอกว่ายืมได้ "1–2 วัน (หรือคืนภายในเวลาปิดทำการของวันที่ยืม)" แต่ไม่ระบุว่าแต่ละประเภท (ปลั๊กไฟ ร่ม ถุงผ้า) ได้กี่วัน และเวลาปิดทำการคือกี่โมง (T-13 รอ)
2. ASM-02 ให้ระบบปฏิเสธอัตโนมัติเมื่อมีรายการค้างคืน แต่ FR-EQP-06 และ AC-EQP-04 บอกว่าเจ้าหน้าที่ต้องตรวจก่อนตัดสินใจ ควรเป็นแบบไหน และใครมีสิทธิ์ override ต้องบันทึกเหตุผลหรือไม่ (T-14 รอ)
3. ระบบยังไม่มีการยืนยันตัวตน (001/002 ยังไม่มีใครทำ) หน้าจอนักศึกษาจะรู้รหัสนักศึกษาจากไหน และเมนูเจ้าหน้าที่ควรแยกสิทธิ์อย่างไร (T-05, T-08 ควรได้คำตอบก่อนเริ่ม)
