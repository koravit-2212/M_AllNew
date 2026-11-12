# RTM: ใช้บริการปริ้นเอกสาร (Printing)
อ้างอิง: spec.md SPEC-PRT-001 Draft v3 (Q-04 ถึง Q-09) | tasks.md (T-01 ถึง T-10 เสร็จ รอทีมตรวจ) | test-cases.md (14 แถวใช้ได้ + 2 แถวร่าง)
สร้างด้วย /verify เมื่อ 2569-11-12 | test: 51 ผ่าน 0 ไม่ผ่าน (pytest 32, vitest 19)

หมายเหตุ: spec 006 ไม่มีบรรทัด "ใช้ร่วม" จึงไม่มี Constraint จาก `specs/000-shared/constraints.md` (ไฟล์ร่วมเป็นของ 001-booking) และไม่มีหมวด "หน้าจอ (UI)" จึงไม่มีข้อความที่ "ต้องตรง" กับ mockup
ช่อง "ทีมตัดสิน" ด้านล่าง AI เขียนแทนตามคำสั่งทีม "ตัดสินใจเองทั้งหมดได้เลย" (2569-11-12) ทีมควรตรวจ

## 1. ตามรอยไปข้างหน้า (requirement ไป โค้ด ไป test)
| ID | AC | task | โค้ด (ไฟล์: ฟังก์ชัน) | test (ผล) | สถานะ |
|---|---|---|---|---|---|
| FR-PRT-01 | AC-PRT-01 | T-02, T-03, T-04 | `api/printing.py: upload_file, print_options`, `services/printing_service.py: register_file, allowed_color_modes`, `pages/PrintPage.jsx` (เลือกไฟล์ ชนิดการพิมพ์ จำนวน) | test_TC_PRT_01_1 (pytest+vitest ผ่าน), 01_2 (pytest+vitest ผ่าน), test_AC_PRT_01_* (ผ่าน) | ครบ |
| FR-PRT-02 | AC-PRT-01 | T-01, T-03, T-04 | `printing_service.py: calculate_cost`, `config.py: PRINT_RATE_PER_PAGE_BAHT` | test_TC_PRT_01_1, 01_2, 01_3 (ผ่าน) | ครบ |
| FR-PRT-03 | AC-PRT-02 | T-05, T-06 | `printing_service.py: submit_print_job, job_payload`, `api/printing.py: submit_print, get_print_job`, `PrintPage.jsx` (ยืนยันและผล) | test_TC_PRT_02_1 (pytest+vitest ผ่าน), 02_2, 02_3 (ผ่าน) TC-PRT-02-4 (คน) ร่าง | ช่องโหว่ (F-02) |
| FR-PRT-04 | AC-PRT-04 | T-09, T-10 | `printing_service.py: validate_file`, `upload_file` (415), `PrintPage.jsx: rejectedFile` | test_TC_PRT_04_1 (pytest+vitest ผ่าน), 04_2, 04_3 (ผ่าน), 04_4 (pytest+vitest ผ่าน), test_TC_PRT_01_4 (ผ่าน) | ช่องโหว่ (F-06) |
| FR-PRT-05 | AC-PRT-03 | T-01, T-07, T-08 | `printing_service.py: ready_printer, submit_print_job` (PrinterNotReady), `api/printing.py: get_printers_status`, `PrintPage.jsx` (เครื่องไม่พร้อม + ลองใหม่) | test_TC_PRT_03_1 (pytest+vitest ผ่าน), 03_2, 03_3 (ผ่าน) | ครบ |
| NFR-USB-01 | ไม่มี AC | T-02, T-04, T-06, T-08, T-10 | `frontend/index.html` (meta viewport), Tailwind `md:` | ไม่มี test อัตโนมัติ TC-PRT-NFR-1 (คน) ยังเป็นร่าง | ช่องโหว่ (F-01) |
| IF-PRN-01 | AC-PRT-02, AC-PRT-03 (ทางอ้อม) | T-01, T-05, T-07 | `models/printing.py: FakePrintSpooler`, `submit_print_job` (`store.spooler.send`) | test_TC_PRT_02_1 (ผ่าน) ตรวจกับ spooler จำลองเท่านั้น | ช่องโหว่ (F-02) |
| CON-FILE-01 | AC-PRT-04 | T-01, T-09, T-10 | `config.py: PRINT_ALLOWED_EXTENSIONS, PRINT_MAX_FILE_SIZE_MB`, `validate_file` | test_TC_PRT_04_1, 04_2, 04_3 (ผ่าน) | ช่องโหว่ (F-06) |

## 2. ตามรอยย้อนกลับ (โค้ด ไป requirement)
| โค้ด (ไฟล์: ฟังก์ชัน หรือ endpoint) | อ้าง ID | ตรงกับข้อความใน spec ไหม | หมายเหตุ |
|---|---|---|---|
| `POST /api/print/upload` | FR-PRT-01, FR-PRT-04, Q-07 | ตรง | รับ JSON ข้อมูลไฟล์แทน multipart (plan แก้แล้ว F-03) |
| `GET /api/print/options` | FR-PRT-01, FR-PRT-02 | ตรง | ต้องส่ง pages / copies / color_mode (plan แก้แล้ว F-05) |
| `POST /api/print/submit` | FR-PRT-03, FR-PRT-05, IF-PRN-01 | ตรง | ไม่มี target_printer_id ไม่ตรวจโควตา (plan แก้แล้ว F-04, Q-04) |
| `GET /api/print/jobs/{id}` | FR-PRT-03 | ตรง | มีใน plan |
| `GET /api/printers/status` | FR-PRT-05, IF-PRN-01 | ตรง | มีใน plan |
| `printing_service.py: COLOR_MODE_LABELS` | FR-PRT-01 | ตรง | ข้อความจาก UI-PRT-01 ไม่ใช่ตัวเลข |
| `config.py: PRINT_*` | CON-FILE-01, ASM-02, ASM-03 | ตรง ตัวเลขตรง spec (6 ชนิด, 50 MB, 1 / 5 บาท) | อยู่ในตาราง "ค่าที่ตั้งได้" ของ plan แล้ว |
| `PrintPage.jsx` ข้อความ "ส่งงานพิมพ์ไม่สำเร็จ กรุณาลองใหม่" | Q-09 | ตรงตาม Q-09 | |
| ข้อความ mockup "หักจากโควตาฟรี 100 บาท/เทอม" | ASM-03 / ASM-04 | ไม่ได้สร้าง | ตาม Q-04 (การหักโควตาไม่อยู่ในรอบนี้) |
| ASM-03 (เพดานหน้า), ASM-04 (หักโควตา) | Q-04, Q-06 | ไม่ได้สร้าง | ไม่มี FR / AC และ Out of scope (การชำระเงิน) |

## 3. ข้อค้นพบ
ชนิด: AC ไม่มี test / test อ่อน / โค้ดไม่มี FR / FR ไม่มี AC / เดา Q-xx / ละเมิด Constraint / ตัวเลขไม่ตรง spec / อ้าง ID ผิดเรื่อง
ทีมตัดสิน: แก้โค้ด / แก้ spec / เพิ่ม Q-xx / ไม่ใช่ปัญหา (พร้อมเหตุผล 1 บรรทัด)

| F-ID | ชนิด | อยู่ที่ | ขัดกับ | รายละเอียด | ทีมตัดสิน |
|---|---|---|---|---|---|
| F-02 | test อ่อน | `backend/app/models/printing.py: FakePrintSpooler`, `PrintPage.jsx: chooseFile` (ส่งเฉพาะข้อมูลไฟล์) | AC-PRT-02, IF-PRN-01 | Then ของ AC-PRT-02 "นักศึกษาได้รับเอกสารตามจำนวนที่กำหนด" ยังไม่มีอะไรตรวจได้จริง เพราะ spooler เป็นตัวจำลอง และระบบไม่ได้รับเนื้อไฟล์ (Q-07) test ตรวจได้แค่ว่า spooler จำลองได้รับงานที่จำนวนหน้า × ชุดถูกต้อง | เพิ่ม Q-xx: Q-07 ใช้ spooler จำลองชั่วคราว รอ endpoint จริงจากฝ่าย IT แล้วค่อยทำ TC-PRT-02-4 |
| F-06 | ละเมิด Constraint | `backend/app/services/printing_service.py: validate_file`, `api/printing.py: UploadIn` | CON-FILE-01 | ระบบตรวจชนิดจากนามสกุลในชื่อไฟล์ และขนาดจากตัวเลขที่หน้าจอส่งมา (Q-07) ไม่ได้ตรวจเนื้อไฟล์จริง ผู้ใช้ตั้งชื่อไฟล์อื่นเป็น .pdf หรือส่งขนาดไม่ตรงได้ เมื่อส่งเนื้อไฟล์จริงต้องตรวจขนาดจริงและชนิดจากเนื้อไฟล์ | เพิ่ม Q-xx: Q-07 ยอมรับชั่วคราว ต้องแก้เมื่อเปลี่ยนเป็นส่งเนื้อไฟล์จริง |
| F-01 | FR ไม่มี AC | `frontend/` ทั้งหมด | NFR-USB-01 | NFR-USB-01 ไม่มี AC และยังไม่มีผลการลองบนมือถือ เพิ่มแถว "คน" TC-PRT-NFR-1 แล้วแต่ยังเป็นร่าง | แก้ spec: เพิ่มแถว TC-PRT-NFR-1 รอทีมตรวจแถวและลองบนมือถือ |

## 4. แก้แล้ว
| F-ID | แก้อย่างไร | รู้ได้อย่างไร |
|---|---|---|
| F-03 | (โค้ดไม่มี FR: upload รับ JSON ไม่ใช่ multipart ตาม plan) แก้ plan ข้อ 4 ให้ตรง Q-07 | เปิด plan ข้อ 4 เทียบกับ `api/printing.py: UploadIn` |
| F-04 | (plan มี target_printer_id และตรวจโควตาตอน submit แต่โค้ดไม่มี) แก้ plan ข้อ 4 ระบุว่าเลือกเครื่องแรกที่พร้อม และไม่ตรวจโควตา (Q-04, Q-06) | เปิด plan ข้อ 4 เทียบกับ `submit_print_job` |
| F-05 | (options ต้องส่ง pages / copies / color_mode แต่ plan ระบุแค่ file_id) แก้ plan ข้อ 4 | เปิด plan ข้อ 4 เทียบกับ `print_options` |
| F-07 | (จุดตรวจเฟส 3 ใน tasks.md อ้าง GET /api/print/jobs ที่ไม่มี) แก้ข้อความจุดตรวจให้ใช้ GET /api/printers/status | เปิด tasks.md จุดตรวจเฟส 3 |
