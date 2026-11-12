# tasks: ใช้บริการปริ้นเอกสาร (Printing)

- Feature: ใช้บริการปริ้นเอกสาร
- Spec ID: SPEC-PRT-001 (`specs/006-printing/spec.md` Draft v2)
- อ้างอิง: `specs/006-printing/plan.md`
- วันที่: 2569-11-12

สรุป
1. มี 5 เฟส (เฟส 0 ถึงเฟส 4) รวม 10 task
2. task ที่ต้องรอ Open Questions: 0 task (spec ไม่มี Q-xx ค้าง แต่มี "ข้อเสนอคำถาม" 3 ข้อท้ายไฟล์)
3. เฟสแรกที่ลองใช้งานได้จริงคือเฟส 1 (เลือกไฟล์ กำหนดจำนวน แล้วเห็นค่าใช้บริการ) ส่วนเฟส 0 ลองได้แค่เมนูสลับหน้า

หมายเหตุทางเทคนิค (ทีมเลือกเอง ไม่ได้มาจาก spec)
- plan.md เลือก PostgreSQL และ object storage แต่โค้ดที่มีอยู่ของ 003 ใช้ข้อมูลในหน่วยความจำ task ชุดนี้ทำตามแนวทางเดียวกับ 003 คือเก็บข้อมูลไฟล์ งานพิมพ์ และสถานะเครื่องพิมพ์ในหน่วยความจำ ไม่เก็บเนื้อไฟล์จริง
- IF-PRN-01 ยังไม่มี endpoint ของ print spooler จากฝ่าย IT จึงทำเป็นตัวเชื่อม spooler จำลองที่จดงานที่ได้รับไว้ (plan.md ข้อ 6 ให้ใช้ mock/stub ในการทดสอบ)
- spec.md ไม่มีหมวด "หน้าจอ (UI)" จึงยังไม่มีข้อความที่ระบุว่า "ต้องตรง" กับ mockup task หน้าจอใช้ข้อความจาก `mockups/UI-PRT-01-print.html` เป็นแนวทาง และทีมควรตรวจด้วยตา

## เฟส 0: ฐานราก (ไม่มี AC เป็นงานพื้นฐาน)

### T-01 กำหนดค่าการพิมพ์ใน config และสร้างที่เก็บงานพิมพ์กับ spooler จำลอง
- รองรับ: CON-FILE-01 (ชนิดและขนาดไฟล์อยู่ใน config), IF-PRN-01 (spooler จำลอง), FR-PRT-02 (อัตราค่าพิมพ์ตาม ASM-01, ASM-03), FR-PRT-05 (สถานะเครื่องพิมพ์)
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-03, T-05, T-07, T-09
- ไฟล์ที่แตะ: `backend/app/config.py`, `backend/app/models/printing.py`, `backend/tests/test_PRT_T01_print_store.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: `test_PRT_T01_print_store.py` ผ่าน โดยยืนยันว่า config มีชนิดไฟล์ 6 ชนิด ขนาดสูงสุด 50 MB อัตราขาว-ดำและสี และที่เก็บเริ่มต้นมีเครื่องพิมพ์สถานะพร้อมใช้งานโดย spooler จำลองยังไม่มีงาน
- สถานะ: เสร็จ รอทีมตรวจ

### T-02 เพิ่มเมนูไปหน้าปริ้นเอกสารใน App.jsx โดยไม่ลบหน้าเดิม
- รองรับ: FR-PRT-01 (จุดเข้าหน้าปริ้น), NFR-USB-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-04
- ไฟล์ที่แตะ: `frontend/src/App.jsx`, `frontend/src/pages/PrintPage.jsx`, `frontend/src/__tests__/App.test.jsx`
- แบบหน้าจอ: UI-PRT-01 `mockups/UI-PRT-01-print.html` (เฉพาะแถบชื่อหน้า "ปริ้นเอกสาร")
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: `App.test.jsx` ผ่าน กดเมนู "ปริ้นเอกสาร" แล้วเห็นหัวข้อ "ปริ้นเอกสาร" และกดกลับเมนู "หนังสือ" แล้วเห็นหน้าค้นหาเดิม
- สถานะ: เสร็จ รอทีมตรวจ

#### จุดตรวจเฟส 0
- test ที่ต้องผ่านทั้งหมด: `test_PRT_T01_print_store.py`, `App.test.jsx` และ test เดิมของ 003 ทั้งหมดต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเอง (ไม่มี AC):
  Given เปิดเว็บที่ port 5173
  When กดเมนู "ปริ้นเอกสาร" แล้วกดเมนู "หนังสือ"
  Then เห็นหัวข้อ "ปริ้นเอกสาร" และกลับมาเห็นหน้าค้นหาหนังสือเดิมได้
- ยังขาด: ไม่มี

## เฟส 1: เห็นตัวเลือกการพิมพ์และค่าใช้บริการก่อนยืนยัน (AC-PRT-01)

### T-03 สร้าง API อัปโหลดไฟล์ที่รองรับและคำนวณค่าใช้บริการ
- รองรับ: FR-PRT-01, FR-PRT-02
- ตรวจด้วย: AC-PRT-01
- ไฟล์ที่แตะ: `backend/app/services/printing_service.py`, `backend/app/api/printing.py`, `backend/app/main.py`, `backend/tests/test_AC_PRT_01_cost_preview.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: `test_AC_PRT_01_CostPreview` ผ่าน (POST /api/print/upload รับไฟล์ PDF แล้วได้ file_id, GET /api/print/options คืนชนิดการพิมพ์ที่เลือกได้ และค่าใช้บริการ = จำนวนหน้า × จำนวนชุด × อัตราของชนิดการพิมพ์)
- สถานะ: พร้อมทำ

### T-04 ทำหน้าเลือกไฟล์ ชนิดการพิมพ์ จำนวนหน้า จำนวนชุด และแสดงค่าใช้บริการ
- รองรับ: FR-PRT-01, FR-PRT-02, NFR-USB-01
- ตรวจด้วย: AC-PRT-01
- ไฟล์ที่แตะ: `frontend/src/api/client.js`, `frontend/src/pages/PrintPage.jsx`, `frontend/src/__tests__/PrintPage.test.jsx`
- แบบหน้าจอ: UI-PRT-01 `mockups/UI-PRT-01-print.html` (สถานะปกติ AC-PRT-01)
- ต้องทำหลัง: T-02, T-03
- เสร็จเมื่อ: test หน้าจอ AC-PRT-01 ผ่าน (ใช้ client จำลอง เลือกไฟล์ กรอก 12 หน้า 2 ชุด แล้วเห็นบรรทัดคำนวณและค่าใช้บริการที่ API ตอบ)
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 1
- test ที่ต้องผ่านทั้งหมด: `test_AC_PRT_01_*` (หลังบ้าน), `PrintPage.test.jsx` (AC-PRT-01) และ test ของเฟส 0 กับ 003 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-PRT-01:
  Given เตรียมไฟล์ PDF ขนาดเล็ก 1 ไฟล์
  When กดเมนู "ปริ้นเอกสาร" เลือกไฟล์นั้น เลือกขาว-ดำ กรอกจำนวนหน้า 12 และจำนวนชุด 2
  Then เห็น "12 หน้า × 2 ชุด = 24 หน้า" และค่าใช้บริการตามอัตราขาว-ดำใน config ก่อนกดถัดไป
- ยังขาด: ไม่มี

## เฟส 2: ส่งงานพิมพ์สำเร็จ (AC-PRT-02)

### T-05 สร้าง API ยืนยันการพิมพ์ ส่งงานไป spooler และบันทึกการใช้บริการ
- รองรับ: FR-PRT-03, IF-PRN-01
- ตรวจด้วย: AC-PRT-02
- ไฟล์ที่แตะ: `backend/app/services/printing_service.py`, `backend/app/api/printing.py`, `backend/tests/test_AC_PRT_02_print_flow.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: `test_AC_PRT_02_PrintFlow` ผ่าน (POST /api/print/submit เมื่อเครื่องพร้อม ได้สถานะ sent, spooler จำลองได้รับงาน 1 งานที่มีจำนวนหน้า × จำนวนชุดตรงกับที่กำหนด และ GET /api/print/jobs/{id} อ่านงานที่บันทึกไว้ได้)
- สถานะ: พร้อมทำ

### T-06 ทำขั้น "ยืนยัน" และหน้าผล "ส่งงานพิมพ์แล้ว"
- รองรับ: FR-PRT-03, NFR-USB-01
- ตรวจด้วย: AC-PRT-02
- ไฟล์ที่แตะ: `frontend/src/api/client.js`, `frontend/src/pages/PrintPage.jsx`, `frontend/src/__tests__/PrintPage.test.jsx`
- แบบหน้าจอ: UI-PRT-01 `mockups/UI-PRT-01-print.html` (สถานะส่งพิมพ์สำเร็จ AC-PRT-02)
- ต้องทำหลัง: T-04, T-05
- เสร็จเมื่อ: test หน้าจอ AC-PRT-02 ผ่าน (กดยืนยันแล้วเห็น "ส่งงานพิมพ์แล้ว" พร้อมชื่อไฟล์ จำนวนหน้ารวม และค่าใช้บริการ)
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 2
- test ที่ต้องผ่านทั้งหมด: `test_AC_PRT_02_*`, test หน้าจอ AC-PRT-02 และ test ของเฟส 0 ถึง 1 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-PRT-02:
  Given เครื่องพิมพ์ใน config เป็นสถานะพร้อมใช้งาน และเลือกไฟล์ PDF กำหนด 12 หน้า 2 ชุดแล้ว
  When กด "ถัดไป" แล้วกดยืนยันการพิมพ์
  Then เห็น "ส่งงานพิมพ์แล้ว" จำนวน 24 หน้า และเปิด GET /api/print/jobs/{id} เห็นงานสถานะ sent
- ยังขาด: ไม่มี

## เฟส 3: เครื่องพิมพ์ไม่พร้อมใช้งาน (AC-PRT-03)

### T-07 ไม่ส่งงานเมื่อเครื่องพิมพ์ไม่พร้อม และเปิด API สถานะเครื่องพิมพ์
- รองรับ: FR-PRT-05, IF-PRN-01
- ตรวจด้วย: AC-PRT-03
- ไฟล์ที่แตะ: `backend/app/services/printing_service.py`, `backend/app/api/printing.py`, `backend/tests/test_AC_PRT_03_printer_not_ready.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-05
- เสร็จเมื่อ: `test_AC_PRT_03_PrinterNotReady` ผ่าน (ตั้งเครื่องเป็น offline แล้ว submit ได้ผลแจ้งเตือน spooler จำลองไม่ได้รับงาน และ GET /api/printers/status แสดงสถานะ offline)
- สถานะ: พร้อมทำ

### T-08 แสดงสถานะ "เครื่องพิมพ์ไม่พร้อมใช้งาน" และปุ่มลองใหม่
- รองรับ: FR-PRT-05, NFR-USB-01
- ตรวจด้วย: AC-PRT-03
- ไฟล์ที่แตะ: `frontend/src/pages/PrintPage.jsx`, `frontend/src/__tests__/PrintPage.test.jsx`
- แบบหน้าจอ: UI-PRT-01 `mockups/UI-PRT-01-print.html` (สถานะเครื่องพิมพ์ไม่พร้อม AC-PRT-03)
- ต้องทำหลัง: T-06, T-07
- เสร็จเมื่อ: test หน้าจอ AC-PRT-03 ผ่าน (เห็น "เครื่องพิมพ์ไม่พร้อมใช้งาน" และปุ่ม "ลองใหม่")
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 3
- test ที่ต้องผ่านทั้งหมด: `test_AC_PRT_03_*`, test หน้าจอ AC-PRT-03 และ test ของเฟส 0 ถึง 2 ต้องยังผ่าน
- เปิดระบบ: แก้สถานะเครื่องพิมพ์ใน `backend/app/config.py` เป็น offline แล้วเปิดหลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-PRT-03:
  Given เครื่องพิมพ์สถานะ offline และเลือกไฟล์ที่รองรับแล้ว
  When กดยืนยันการพิมพ์
  Then เห็น "เครื่องพิมพ์ไม่พร้อมใช้งาน" และ GET /api/print/jobs ไม่มีงานสถานะ sent เพิ่ม
- ยังขาด: ไม่มี

## เฟส 4: ไฟล์ไม่รองรับ (AC-PRT-04)

### T-09 ปฏิเสธไฟล์ที่ชนิดหรือขนาดไม่ตรง CON-FILE-01
- รองรับ: FR-PRT-04, CON-FILE-01
- ตรวจด้วย: AC-PRT-04
- ไฟล์ที่แตะ: `backend/app/services/printing_service.py`, `backend/app/api/printing.py`, `backend/tests/test_AC_PRT_04_unsupported_file.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: `test_AC_PRT_04_UnsupportedFile` ผ่าน (อัปโหลด .exe และไฟล์เกิน 50 MB ได้ผลแจ้งเตือน ไม่ได้ file_id และเรียก options/submit ต่อไม่ได้)
- สถานะ: พร้อมทำ

### T-10 แสดงคำเตือนไฟล์ไม่รองรับและปิดปุ่มถัดไป
- รองรับ: FR-PRT-04, CON-FILE-01, NFR-USB-01
- ตรวจด้วย: AC-PRT-04
- ไฟล์ที่แตะ: `frontend/src/pages/PrintPage.jsx`, `frontend/src/__tests__/PrintPage.test.jsx`
- แบบหน้าจอ: UI-PRT-01 `mockups/UI-PRT-01-print.html` (สถานะไฟล์ไม่รองรับ AC-PRT-04)
- ต้องทำหลัง: T-04, T-09
- เสร็จเมื่อ: test หน้าจอ AC-PRT-04 ผ่าน (เลือก setup.exe แล้วเห็น "ไม่รองรับไฟล์ชนิดนี้" และปุ่ม "ถัดไป" กดไม่ได้)
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 4
- test ที่ต้องผ่านทั้งหมด: `test_AC_PRT_04_*`, test หน้าจอ AC-PRT-04 และ test ของเฟส 0 ถึง 3 ต้องยังผ่าน
- เปิดระบบ: หลังบ้าน `cd backend && uvicorn app.main:app --reload --port 8000` หน้าจอ `cd frontend && npm run dev`
- คนลองเองตาม AC-PRT-04:
  Given เตรียมไฟล์ .exe หรือ .zip 1 ไฟล์
  When เลือกไฟล์นั้นในหน้าปริ้นเอกสาร
  Then เห็น "ไม่รองรับไฟล์ชนิดนี้" พร้อมรายการชนิดที่รองรับ และกดถัดไปไม่ได้
- ยังขาด: ไม่มี

## ตารางตรวจความครบ

### 1. AC กับ task
| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-PRT-01 | T-03, T-04 |
| AC-PRT-02 | T-05, T-06 |
| AC-PRT-03 | T-07, T-08 |
| AC-PRT-04 | T-09, T-10 |

### 2. Constraint กับ task
| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| IF-PRN-01 | T-01, T-05, T-07 |
| CON-FILE-01 | T-01, T-09, T-10 |

หมายเหตุ: Constraint ใน `specs/000-shared/constraints.md` ระบุผู้อ้างเป็น 001-booking เท่านั้น และ spec ของ 006 ไม่มีบรรทัด "ใช้ร่วม" จึงไม่นับเป็น Constraint ของฟีเจอร์นี้

### 3. FR กับ AC
| FR ID | AC ที่ตรวจ FR นี้ | เฟส |
|---|---|---|
| FR-PRT-01 | AC-PRT-01 | เฟส 0, 1 |
| FR-PRT-02 | AC-PRT-01 | เฟส 1 |
| FR-PRT-03 | AC-PRT-02 | เฟส 2 |
| FR-PRT-04 | AC-PRT-04 | เฟส 4 |
| FR-PRT-05 | AC-PRT-03 | เฟส 3 |

## สิ่งที่ยังไม่ทำ

Open Questions ใน spec: ไม่มี (Q-01 ถึง Q-03 ตอบแล้วเป็น ASM-02 ถึง ASM-04)

ข้อเสนอคำถามให้ทีม (ยังไม่ใช่ Q-xx ทีมต้องตัดสินว่าจะเพิ่มใน spec หรือไม่)
1. ASM-04 ให้หักโควตาจาก SU-IT Account เมื่อสั่งพิมพ์ แต่ Out of scope บอกว่าการชำระเงินไม่อยู่ในขอบเขต และไม่มี FR หรือ AC เรื่องหักโควตา task ชุดนี้จึงคำนวณและแสดงค่าใช้บริการเท่านั้น ไม่หักโควตา ทีมต้องการเพิ่ม FR หรือไม่
2. จำนวนหน้าให้ผู้ใช้กรอกเอง (ตาม mockup) ระบบไม่นับหน้าจากไฟล์ ทีมยืนยันหรือไม่
3. ASM-03 ให้พิมพ์ขาว-ดำได้สูงสุด 100 หน้า/เทอม และสีสูงสุด 20 หน้า/เทอม แต่ไม่มี FR หรือ AC เรื่องเพดานนี้ จึงไม่มี task
