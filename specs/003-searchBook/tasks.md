# Tasks: ค้นหาหนังสือ (Book Search)
Feature: ค้นหาหนังสือ (Book Search) | Spec ID: SPEC-SRC-001 | อ้างอิง: specs/003-searchBook/plan.md | วันที่: 2026-11-12

## สรุป
- มี 5 เฟสหลักในการพัฒนาฟีเจอร์นี้แบบ vertical slice
- มี 11 task ทั้งหมด
- มี 0 task ที่ต้องรอ Open Questions
- เฟสแรกที่ลองใช้งานได้จริง: เฟส 1 (ค้นหาหนังสือสำเร็จตามคำค้น)

## เฟส 0: ฐานรากข้อมูลและจุดเชื่อมต่อ (IF-CAT-01)

### T-01 สร้างโครงข้อมูล BookTitle/BookCopy และข้อมูลตัวอย่างสำหรับค้นหา
- รองรับ: FR-SRC-01, FR-SRC-02, FR-SRC-03, IF-CAT-01
- ตรวจด้วย: AC-SRC-01, AC-SRC-04
- ไฟล์ที่แตะ: backend/app/models/book.py, backend/app/config.py
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: มีข้อมูลตัวอย่างหนังสือให้ค้นหาได้จริงและมีข้อมูลจำลอง per-copy ที่รองรับสถานะว่าง/ถูกยืมพร้อมตำแหน่งจัดเก็บ
- สถานะ: พร้อมทำ

### T-02 ตั้งค่า Search Index contract และ health probe สำหรับคอนโทรลสถานะ
- รองรับ: FR-SRC-01, FR-SRC-05, IF-CAT-01
- ตรวจด้วย: AC-SRC-03
- ไฟล์ที่แตะ: backend/app/services/search_index.py, backend/app/api/health.py, backend/app/main.py
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: API health/search สามารถบอก index status และ last sync time ได้เพื่อใช้งานตรวจสอบ partial results และข้อมูลให้ผลบางส่วน
- สถานะ: พร้อมทำ

### T-03 พัฒนาตัวประมวลผลค้นหาพื้นฐานแบบ backend API
- รองรับ: FR-SRC-01, FR-SRC-02, NFR-PRF-03, IF-CAT-01
- ตรวจด้วย: AC-SRC-01
- ไฟล์ที่แตะ: backend/app/api/search.py, backend/app/services/search_service.py
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01, T-02
- เสร็จเมื่อ: API GET /api/search?q={q}&page={n}&per_page={m} คืนผลลัพธ์แบบ title-level พร้อม pagination, relevance, และ aggregated availability
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 0
- test ที่ต้องผ่านทั้งหมด: test_AC_SRC_01_performance_and_relevance (หลังจากเสร็จเงื่อนไขด้าน UI/UI ต่อเนื่อง), test_AC_SRC_04_book_detail_fields
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตามสภาพแวดล้อมที่จำเป็น:
  Given มีข้อมูลหนังสือตัวอย่างหลายเล่มพร้อมสถานะว่าง/ถูกยืม
  When เรียก API /api/search และ /api/books/{title_id} เริ่มต้น
  Then ระบบต้องสามารถอ่าน data model พื้นฐานและพร้อมสำหรับขยายไปสู่ UI ต่อไป
- ยังขาด: ไม่มี

## เฟส 1: ค้นหาหนังสือสำเร็จตามคำค้น (AC-SRC-01)

### T-04 สร้างหน้า Search Page และเรียก API ค้นหาแบบ fuzzy/partial match
- รองรับ: FR-SRC-01, FR-SRC-02, AC-SRC-01
- ตรวจด้วย: AC-SRC-01
- ไฟล์ที่แตะ: frontend/src/pages/SearchPage.jsx, frontend/src/api/client.js
- แบบหน้าจอ: UI-SRC-01 mockups/UI-SRC-01-search-results.html
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: ผู้ใช้พิมพ์คำค้นที่คล้ายกัน เช่น "clen cod" แล้วเห็นผลลัพธ์ที่ตรงกับคำค้นแบบ pagination และมีสถานะสรุปต่อ title
- สถานะ: พร้อมทำ

### T-05 ทดสอบและจัดการกรณีคำค้นไม่มีผลลัพธ์บนหน้า Search
- รองรับ: FR-SRC-04, AC-SRC-02
- ตรวจด้วย: AC-SRC-02
- ไฟล์ที่แตะ: frontend/src/pages/SearchPage.jsx, backend/app/api/search.py
- แบบหน้าจอ: UI-SRC-01 mockups/UI-SRC-01-search-results.html
- ต้องทำหลัง: T-03, T-04
- เสร็จเมื่อ: เมื่อค้นหาคำที่ไม่มีผล ระบบแสดงข้อความ "ไม่พบข้อมูลหนังสือ" และไม่แสดงรายการที่ผิดพลาด
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 1
- test ที่ต้องผ่านทั้งหมด: test_AC_SRC_01_performance_and_relevance, test_AC_SRC_02_no_results
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-SRC-01:
  Given ใช้คำค้นที่มีข้อมูลจริงแต่พิมพ์คลาดเล็กน้อย เช่น "clen cod"
  When ผู้ใช้กดค้นหา
  Then ระบบต้องแสดงรายการหนังสือที่ตรงกับคำค้นภายในเวลาที่กำหนด พร้อมแสดงสถานะสรุปแบบ aggregated per-title และมี pagination 20–25 รายการต่อหน้า
- ยังขาด: ไม่มี

## เฟส 2: แจ้ง “ไม่พบข้อมูลหนังสือ” เมื่อไม่มีผลลัพธ์ (AC-SRC-02)

### T-06 ปรับ API search ให้ตอบเป็นข้อความผิดพลาดแบบ no-result
- รองรับ: FR-SRC-04, AC-SRC-02
- ตรวจด้วย: AC-SRC-02
- ไฟล์ที่แตะ: backend/app/api/search.py, backend/app/services/search_service.py
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: API response สำหรับคำค้นไม่มีผลเริ่มจาก empty list พร้อม signal หรือข้อความ "ไม่พบข้อมูลหนังสือ" ที่ UI ใช้ได้
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 2
- test ที่ต้องผ่านทั้งหมด: test_AC_SRC_02_no_results
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-SRC-02:
  Given ไม่มีหนังสือที่ตรงกับคำค้น เช่น "xyzqwe"
  When ผู้ใช้กดค้นหา
  Then ระบบแสดงข้อความ "ไม่พบข้อมูลหนังสือ" อย่างชัดเจนบนหน้า Search Page
- ยังขาด: ไม่มี

## เฟส 3: กรณีฐานข้อมูลช้า/ไม่ครบ และแสดงผลลัพธ์บางส่วน (AC-SRC-03)

### T-07 เพิ่ม partial-results handling ใน Search API
- รองรับ: FR-SRC-05, AC-SRC-03
- ตรวจด้วย: AC-SRC-03
- ไฟล์ที่แตะ: backend/app/api/search.py, backend/app/services/search_service.py
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-02, T-03
- เสร็จเมื่อ: หาก DB ตอบช้าหรือคืนผลลัพธ์บางส่วน API ยังสามารถส่งผลลัพธ์ที่มีได้ทันทีและตั้ง flag partial=true พร้อมข้อความเตือนที่ UI ใช้ได้
- สถานะ: พร้อมทำ

### T-08 เพิ่มแจ้งเตือน partial results บนหน้า Search Page
- รองรับ: FR-SRC-05, AC-SRC-03
- ตรวจด้วย: AC-SRC-03
- ไฟล์ที่แตะ: frontend/src/pages/SearchPage.jsx, frontend/src/api/client.js
- แบบหน้าจอ: UI-SRC-01 mockups/UI-SRC-01-search-results.html
- ต้องทำหลัง: T-04, T-07
- เสร็จเมื่อ: เมื่อ API ส่ง partial=true ผู้ใช้เห็นข้อความ "แสดงผลลัพธ์บางส่วน" และยังสามารถดูรายการที่ได้รับได้
- สถานะ: พร้อมทำ

### T-09 เพิ่ม fallback เมื่อ Central DB ไม่พร้อมใช้งาน
- รองรับ: FR-SRC-05, AC-SRC-03
- ตรวจด้วย: AC-SRC-03
- ไฟล์ที่แตะ: backend/app/api/search.py, backend/app/services/search_service.py, frontend/src/pages/SearchPage.jsx
- แบบหน้าจอ: UI-SRC-01 mockups/UI-SRC-01-search-results.html
- ต้องทำหลัง: T-07, T-08
- เสร็จเมื่อ: หากฐานข้อมูลหนังสือไม่สามารถให้ผลใด ๆ ได้ ระบบแจ้งผู้ใช้ว่า "ฐานข้อมูลหนังสือไม่พร้อมใช้งาน" แทนการปิดบริการทั้งหมด
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 3
- test ที่ต้องผ่านทั้งหมด: test_AC_SRC_03_partial_results_and_db_unavailable
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-SRC-03:
  Given ฐานข้อมูลหนังสือตอบช้า หรือให้ผลลัพธ์บางส่วน
  When นักศึกษากดค้นหา
  Then ระบบแสดงผลที่สามารถดึงได้ทันทีพร้อมข้อความเตือนว่าเป็นผลลัพธ์บางส่วน และเมื่อ DB ไม่พร้อมเลยให้แจ้งว่า "ฐานข้อมูลหนังสือไม่พร้อมใช้งาน"
- ยังขาด: ไม่มี

## เฟส 4: ดูรายละเอียดหนังสือแบบ per-copy พร้อมตำแหน่งจัดเก็บ (AC-SRC-04)

### T-10 สร้าง API รายละเอียดหนังสือแบบ per-copy จาก Central DB
- รองรับ: FR-SRC-02, FR-SRC-03, IF-CAT-01
- ตรวจด้วย: AC-SRC-04
- ไฟล์ที่แตะ: backend/app/api/books.py, backend/app/services/book_detail_service.py
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: API GET /api/books/{title_id} ส่งข้อมูลหนังสือพร้อมชื่อ ผู้แต่ง ISBN หมวดหมู่ และรายการสำเนาแต่ละเล่มพร้อมสถานะและตำแหน่งจัดเก็บ
- สถานะ: พร้อมทำ

### T-11 สร้างหน้า Book Detail Page ตาม mockup และเชื่อมต่อ API
- รองรับ: FR-SRC-02, FR-SRC-03, AC-SRC-04
- ตรวจด้วย: AC-SRC-04
- ไฟล์ที่แตะ: frontend/src/pages/BookDetailPage.jsx, frontend/src/api/client.js
- แบบหน้าจอ: UI-SRC-02 mockups/UI-SRC-02-book-detail.html
- ต้องทำหลัง: T-04, T-10
- เสร็จเมื่อ: เมื่อลองเลือกหนังสือจากผลลัพธ์ ระบบแสดงรายละเอียดหนังสือครบถ้วนตามฟิลด์ขั้นต่ำและสถานะรายเล่ม per-copy พร้อมตำแหน่งจัดเก็บ
- สถานะ: พร้อมทำ

#### จุดตรวจเฟส 4
- test ที่ต้องผ่านทั้งหมด: test_AC_SRC_04_book_detail_fields
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-SRC-04:
  Given นักศึกษากดเลือกหนังสือจากรายการผลลัพธ์
  When เปิดหน้า Book Detail Page
  Then ระบบแสดงรายละเอียดหนังสืออย่างครบถ้วน โดยมีอย่างน้อย ชื่อ ผู้แต่ง เลขเรียกหนังสือ/ISBN หมวดหมู่ สถานะยืม-คืน และตำแหน่งจัดเก็บบนชั้น
- ยังขาด: ไม่มี

## ตารางตรวจความครบ

### 1) AC ID | task ที่ตรวจ AC นี้
| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-SRC-01 | T-03, T-04, T-05 |
| AC-SRC-02 | T-05, T-06 |
| AC-SRC-03 | T-07, T-08, T-09 |
| AC-SRC-04 | T-10, T-11 |

### 2) Constraint ID | task ที่ทำให้เป็นจริง
| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| IF-CAT-01 | T-01, T-02, T-03, T-07, T-09, T-10 |

### 3) FR ID | AC ที่ตรวจ FR นี้ | เฟส
| FR ID | AC ที่ตรวจ FR นี้ | เฟส |
|---|---|---|
| FR-SRC-01 | AC-SRC-01 | เฟส 1 |
| FR-SRC-02 | AC-SRC-01, AC-SRC-04 | เฟส 1, เฟส 4 |
| FR-SRC-03 | AC-SRC-04 | เฟส 4 |
| FR-SRC-04 | AC-SRC-02 | เฟส 2 |
| FR-SRC-05 | AC-SRC-03 | เฟส 3 |

## สิ่งที่ยังไม่ทำ
- Open Questions ใน spec.md: ไม่มี
- task ที่รอคำตอบ/รอ Q-xx: ไม่มี

