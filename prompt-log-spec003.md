# Prompt Log - spec 003: Book Search

## 2026-09-20 15:30 คำสั่ง: /clarify

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/spec.md (v1 -> v2)

### คำถามที่ AI ถาม (ทั้งหมด)

1. เวลาที่กำหนดสำหรับการค้นหาเท่าไหร่ (เช่น X วินาที) และรองรับผู้ใช้พร้อมกันกี่คน?
2. ต้องรองรับการค้นหาแบบ fuzzy/typo-tolerant หรือไม่ (เช่น fuzzy, soundex, n-gram)?
3. ขอบเขตฟิลด์ที่ต้องค้นหาให้ชัดเจน: title, author, keywords, ISBN หรืออื่นๆ รวมถึงการแมตช์ (partial word, whole word, case)?
4. สถานะ "ว่าง/ถูกยืม" ให้แสดงระดับใด: per-copy หรือ aggregated per-title?
5. เมื่อฐานข้อมูลกลางตอบช้า/ให้ผลไม่ครบ (partial results) ควรทำอย่างไร: แสดงผลที่มีพร้อมแจ้งเตือน, หยุดแสดงผลและแจ้งว่าไม่พร้อม, หรือใช้ข้อมูลแคช?
6. ค่าที่ยอมรับได้สำหรับ "ใกล้เคียง Real-time" ใน ASM-01 (เช่น staleness ≤ X วินาที)?
7. ในหน้ารายละเอียดหนังสือ ต้องแสดงฟิลด์ไหนบ้างนอกเหนือจากที่ระบุ (เช่น ISBN, ปีพิมพ์, สถานะสำรอง/ตำแหน่งย่อย)?
8. ต้องมีการแบ่งหน้า/จำกัดจำนวนผลลัพธ์ต่อหน้า และค่า default ของการเรียงลำดับหรือไม่?

### คำตอบของทีมและเหตุผล

1. Q2 (Fuzzy Search): ควรใช้ Fuzzy/Partial Match เพื่ออำนวยความสะดวกในการค้นหาหนังสือและตรวจสอบสถานะ
2. Q3 (ขอบเขตฟิลด์ค้นหา): ค้นหาครอบคลุม Title, Author, Keywords และ ISBN/รหัสหนังสือ โดยใช้ partial match และ case-insensitive
3. Q4 (การแสดงสถานะว่าง/ถูกยืม): แสดงระดับ Per-copy (สถานะและตำแหน่งเล่ม) ในหน้ารายละเอียด และ Aggregated Overview ในหน้ารายการค้นหา เพื่อรองรับการยืมผ่านเครื่องอัตโนมัติ/เคาน์เตอร์
4. Q5 (ฐานข้อมูลตอบช้า/partial results): แสดงผลที่มีพร้อมแจ้งเตือนผู้ใช้ เพื่อให้ระบบสามารถให้บริการได้อย่างต่อเนื่อง
5. Q7 (ฟิลด์หน้ารายละเอียด): แสดงชื่อหนังสือ, ผู้แต่ง, เลขเรียกหนังสือ/ISBN, หมวดหมู่, สถานะยืม-คืน, และตำแหน่งจัดเก็บบนชั้น
6. Q8 (Pagination/Default Sort): ใช้ Pagination 20–25 รายการต่อหน้า รองรับทั้งบนคอมพิวเตอร์และมือถือ โดยเรียงลำดับตามความเกี่ยวข้อง (Relevance) เป็นหลัก
7. Q1, Q6 (เวลาที่กำหนด / staleness): ยังไม่ได้ตอบ — ยังคงเป็น Open Question ที่ต้องถามห้องสมุด/ฝ่าย IT เพื่อกำหนดค่าเป็น NFR-PRF-03

### สิ่งที่แก้ใน specs/003-searchBook/spec.md (v1 -> v2)

- เปลี่ยน Status เป็น Draft v2 และอัปเดตวันที่เป็น 2569-09-20
- ปรับ `FR-SRC-01` ให้ระบุชัดเจนว่ารองรับ fuzzy/partial match (case-insensitive) และระบุฟิลด์ที่ค้นหาได้: title, author, keywords, ISBN
- ปรับ `FR-SRC-02` ให้ชัดว่าหน้ารายการแสดงสถานะแบบ aggregated per-title และหน้ารายละเอียดแสดงสถานะแบบ per-copy พร้อมตำแหน่งจัดเก็บ
- ขยาย `FR-SRC-03` ให้ระบุฟิลด์ขั้นต่ำในหน้ารายละเอียด (ชื่อ ผู้แต่ง เลขเรียกหนังสือ/ISBN หมวดหมู่ สถานะยืม-คืน ตำแหน่งจัดเก็บ)
- ปรับ `FR-SRC-05` ให้เป็นการแสดงผล partial results พร้อมแจ้งเตือนผู้ใช้ แทนการปิดการให้บริการทั้งหมด
- ปรับ `AC-SRC-01` เพื่อระบุการแบ่งหน้า (20–25 รายการต่อหน้า) และการเรียงตาม relevance
- ปรับ `AC-SRC-03` เพื่อรองรับการแสดง partial results พร้อมการแจ้งเตือน และกรณีฐานข้อมูลไม่ให้ผลใดๆ ให้แจ้งว่า DB ไม่พร้อมใช้งาน
- เพิ่ม `ASM-02` ถึง `ASM-07` บันทึกคำตัดสินใจของทีม (fuzzy, ขอบเขตฟิลด์, รูปแบบการแสดงสถานะ, partial results, ฟิลด์รายละเอียดขั้นต่ำ, pagination)

### สิ่งที่แก้เพิ่มเติมใน specs/003-searchBook/spec.md (ตอบ Q1 ระบุ performance)

- ปรับ `NFR-PRF-03` ให้ชัดเจนเป็น Response Time 2–3 วินาที และรองรับผู้ใช้งานพร้อมกันอย่างน้อย 500 คน
- เพิ่ม `ASM-08` บันทึกการตัดสินใจเรื่อง performance

---

## 2026-09-20 15:40 คำสั่ง: /clarify (ตอบ Q1)

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/spec.md (v2)

### คำถามที่ AI ถาม

1. เวลาที่กำหนดสำหรับการค้นหาเท่าไหร่ (เช่น X วินาที) และรองรับผู้ใช้พร้อมกันกี่คน?

### คำตอบของทีมและเหตุผล

1. Q1: รองรับผู้ใช้งานพร้อมกันอย่างน้อย 500 คน โดยกำหนด Response Time ไม่เกิน 2–3 วินาที เพื่อให้ตอบสนองอย่างรวดเร็ว

### สิ่งที่แก้เพิ่มเติมใน specs/003-searchBook/spec.md (ตอบ Q1)

- ปรับ `NFR-PRF-03` ให้ชัดเจนเป็น Response Time 2–3 วินาที และรองรับผู้ใช้งานพร้อมกันอย่างน้อย 500 คน
- เพิ่ม `ASM-08` บันทึกการตัดสินใจเรื่อง performance

---

## 2026-09-20 15:50 คำสั่ง: /plan

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/plan.md (สร้างจาก specs/003-searchBook/spec.md)

### ผลลัพธ์

1. สร้างไฟล์ `specs/003-searchBook/plan.md` ซึ่งประกอบด้วย: สรุปแนวทาง, เทคโนโลยีที่เลือก, โมเดลข้อมูล, API/หน้าจอ, ตารางตรวจ Constraints, แผนทดสอบจาก AC, ลำดับงาน และรายการ Open Questions (ขณะนี้ไม่มี Open Questions)
2. สรุปข้อสังเกตสั้น ๆ ที่รายงานกับทีม:
  - Constraint ที่ยังไม่ได้ใช้: ไม่มี (IF-CAT-01 ถูกนำไปใช้)
  - AC ที่ทดสอบยาก: `AC-SRC-01` (performance & concurrency ≥500) และ `AC-SRC-03` (จำลอง partial DB responses)
  - สิ่งที่อยากเดาแต่ไม่ได้เดา: การเลือก Search engine (Elasticsearch vs DB FTS), นโยบาย sync frequency, TTL ของ cache

---

## 2026-11-12 12:00 คำสั่ง: /tasks

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/spec.md
- ผลลัพธ์: สร้างไฟล์ `specs/003-searchBook/tasks.md` พร้อมแยกงานเป็น 5 เฟส และ 11 task
- สรุปผลลัพธ์:
  - เฟสทั้งหมด: 5 เฟส
  - task ทั้งหมด: 11 task
  - task ที่รอ Q-xx: 0 task
  - เฟสแรกที่ลองใช้งานได้จริง: เฟส 1 (`AC-SRC-01`)
- ข้อสังเกต: feature นี้ไม่มี Open Questions ใน spec.md ปัจจุบัน จึงไม่มี task ที่กำหนดสถานะ "รอ Q-xx"
- ตารางตรวจความครบและ traceability ได้รวมไว้ใน `tasks.md` เสร็จสิ้น

---

## 2026-11-12 12:30 คำสั่ง: /implement T-01 003-searchBook

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์ที่สร้าง/แก้: `backend/app/config.py`, `backend/app/models/book.py`, `backend/app/__init__.py`, `backend/app/models/__init__.py`, `backend/tests/test_AC_SRC_01_book_seed_data.py`
- ผลลัพธ์ test:
  - `/workspaces/M_AllNew/.venv/bin/pytest -q tests/test_AC_SRC_01_book_seed_data.py`
  - ผลลัพธ์: `2 passed in 0.01s`
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี — ข้อกำหนดใน spec, plan, and tasks ถูกอ่านครบและตรงกับ task ที่เลือก
- สิ่งที่ทำให้เป็นจริง:
  - `BookTitle` และ `BookCopy` ถูกสร้างใน `backend/app/models/book.py` พร้อม `aggregated_availability` และ `as_detail_payload()` สำหรับ FR-SRC-01/02/03
  - `BOOK_SEARCH_SEED_DATA` และ `SEARCH_PAGE_SIZE_MIN/MAX` ถูกจัดเก็บใน `backend/app/config.py` เพื่อให้ค่าการค้นหาและ pagination มีจุดศูนย์กลางตาม spec
  - ข้อมูลตัวอย่างประกอบด้วย title, authors, keywords, isbn, call_number, copies, shelf location เพื่อรองรับ AC-SRC-01 และ AC-SRC-04

---

## 2026-11-12 12:45 คำสั่ง: /implement T-02

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์ที่สร้าง/แก้: `backend/app/services/search_index.py`, `backend/app/api/health.py`, `backend/app/api/__init__.py`, `backend/app/services/__init__.py`, `backend/app/main.py`, `backend/tests/test_AC_SRC_03_search_health.py`
- ผลลัพธ์ test:
  - `/workspaces/M_AllNew/.venv/bin/pytest -q tests/test_AC_SRC_03_search_health.py`
  - ผลลัพธ์: `1 passed, 1 warning in 0.76s`
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี — ข้อกำหนดใน spec, plan, และ task ชัดเจนว่าต้องมี health endpoint สำหรับ index status และ last sync time
- สิ่งที่ทำให้เป็นจริง:
  - `SearchIndexStatus` และ `get_search_index_health()` ใน `backend/app/services/search_index.py` คืนค่า `index_status`, `last_sync_time`, และ `sync_health` ตาม contract ของ plan
  - `GET /api/health/search` ถูกติดตั้งใน `backend/app/api/health.py` และ `backend/app/main.py` ให้พร้อมเรียกผ่าน FastAPI
  - test `test_AC_SRC_03_search_health_reports_index_status_and_sync_details` ตรวจ `Given / When / Then` ตาม AC-SRC-03 โดยยืนยันการตอบกลับมีข้อมูลสถานะและเวลา sync ที่จำเป็น

---

## 2026-11-12 17:00 คำสั่ง: /implement T-06

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/tasks.md
- ไฟล์ที่สร้าง/แก้: backend/app/api/search.py, backend/app/services/search_service.py, backend/tests/test_AC_SRC_02_no_results.py
- สรุปงาน: ปรับ API /api/search ให้คืน results: [] พร้อม message "ไม่พบข้อมูลหนังสือ" เมื่อคำค้นไม่มีผล และยืนยันว่า UI สามารถใช้ข้อมูลนี้ได้โดยไม่แสดงรายการเก่า
- ผล test: `cd /workspaces/M_AllNew/backend && . ../.venv/bin/activate && pytest -q tests/test_AC_SRC_02_no_results.py && cd /workspaces/M_AllNew/frontend && npm test -- --run` → Backend 1 passed, Frontend 4 passed, exit code 0
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี; ใช้ spec.md / tasks.md เป็นแหล่งความจริง และยึด AC-SRC-02 อย่างตรงไปตรงมา

## 2026-11-12 17:25 คำสั่ง: /implement T-07

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/tasks.md
- ไฟล์ที่สร้าง/แก้: backend/app/api/search.py, backend/app/services/search_service.py, backend/tests/test_AC_SRC_03_partial_results.py
- สรุปงาน: เพิ่ม contract สำหรับ partial-results ใน Search API โดยคืน partial: true, message: "แสดงผลลัพธ์บางส่วน", และ warning เพื่อให้ UI สามารถแจ้งเตือนผู้ใช้ได้โดยไม่ปิดบริการทั้งหมด
- ผล test: `cd /workspaces/M_AllNew/backend && . ../.venv/bin/activate && pytest -q tests/test_AC_SRC_03_partial_results.py` → 1 passed, exit code 0
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี; task นี้มีความชัดเจนจาก AC-SRC-03 และไม่ได้แตะ T-08/T-09

## 2026-11-12 17:40 คำสั่ง: /implement T-08

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/tasks.md
- ไฟล์ที่สร้าง/แก้: frontend/src/__tests__/SearchPage.test.jsx
- สรุปงาน: ปรับ regression test ให้ครอบคลุมสถานะ partial results บนหน้า Search Page โดยต้องแสดงข้อความ “แสดงผลลัพธ์บางส่วน” พร้อมผลลัพธ์ที่สามารถใช้งานได้ต่อไป
- ผล test: `cd /workspaces/M_AllNew/frontend && npm test -- --run` → 2 files passed, 4 tests passed, exit code 0
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี; mockup UI-SRC-01 ชัดเจนว่าควรมี banner แบบ amber และยังมีรายการผลลัพธ์ที่ใช้งานได้

## 2026-11-12 18:00 คำสั่ง: /implement T-09

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/tasks.md
- ไฟล์ที่สร้าง/แก้: backend/app/api/search.py, backend/app/services/search_service.py, frontend/src/pages/SearchPage.jsx, frontend/src/__tests__/SearchPage.test.jsx
- สรุปงาน: เพิ่ม branching ระหว่าง no-result, partial result, และ database unavailable; สำหรับกรณี DB ล่ม API จะคืน message "ฐานข้อมูลหนังสือไม่พร้อมใช้งาน" และหน้า Search Page จะแสดงเฉพาะข้อความนั้น ไม่แสดงผลผิดพลาดหรือ banner partial
- ผล test: `cd /workspaces/M_AllNew/backend && . ../.venv/bin/activate && pytest -q tests/test_AC_SRC_03_partial_results_and_db_unavailable.py && cd /workspaces/M_AllNew/frontend && npm test -- --run` → Backend 1 passed, Frontend 2 files passed / 5 tests passed, exit code 0
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี; spec และ mockup ชัดเจนว่าควรแยก “ไม่มีผลลัพธ์” กับ “ฐานข้อมูลไม่พร้อมใช้งาน” อย่างชัดเจน

## 2026-11-12 19:05 คำสั่ง: /implement T-10

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/tasks.md
- ไฟล์ที่สร้าง/แก้: backend/app/api/books.py, backend/app/services/book_detail_service.py, backend/app/main.py, backend/tests/test_AC_SRC_04_book_detail_fields.py
- สรุปงาน: สร้าง API GET /api/books/{title_id} เพื่อคืนรายละเอียดหนังสือแบบ per-copy จากชุดข้อมูล Central DB ตัวอย่าง โดยมี title, authors, isbn, call_number, category, copies, และ aggregated availability; route ถูกติดตั้งใน FastAPI app และคืน 404 เมื่อไม่พบ title_id
- ผล test: `cd /workspaces/M_AllNew/backend && . ../.venv/bin/activate && pytest -q tests` → 8 passed, exit code 0
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี; spec ระบุชัดเจนว่า AC-SRC-04 ต้องมีชื่อ ผู้แต่ง เลขเรียกหนังสือ/ISBN หมวดหมู่ สถานะยืม-คืน และตำแหน่งจัดเก็บ และโครงสร้างข้อมูลมีอยู่แล้วใน model/book.py และ config.py

## 2026-11-12 19:45 คำสั่ง: /implement T-11

- เครื่องมือ: Copilot ใน Codespaces
- ไฟล์: specs/003-searchBook/tasks.md
- ไฟล์ที่สร้าง/แก้: frontend/src/pages/BookDetailPage.jsx, frontend/src/api/client.js, frontend/src/App.jsx, frontend/src/pages/SearchPage.jsx, frontend/src/__tests__/BookDetailPage.test.jsx
- สรุปงาน: สร้าง Book Detail Page ตาม mockup UI-SRC-02 และเชื่อมต่อกับ API GET /api/books/{title_id}; เมื่อเลือกหนังสือจาก Search Page จะเปิดหน้า detail ที่แสดงชื่อ ผู้แต่ง เลขเรียกหนังสือ ISBN หมวดหมู่ สถานะรวม และรายการ per-copy พร้อมตำแหน่งจัดเก็บ
- ผล test: `cd /workspaces/M_AllNew/backend && . ../.venv/bin/activate && pytest -q tests && cd /workspaces/M_AllNew/frontend && npm test -- --run` → Backend 8 passed, Frontend 3 files passed / 7 tests passed, exit code 0
- สิ่งที่เกือบต้องเดาแต่ถามแทน: ไม่มี; mockup UI-SRC-02 และ spec ระบุชัดเจนว่าฟิลด์ขั้นต่ำและลำดับข้อมูลต้องตรงตามสี่องค์ประกอบหลัก: ชื่อ ผู้แต่ง เลขเรียกหนังสือ/ISBN หมวดหมู่ และสถานะรายเล่มพร้อมตำแหน่งจัดเก็บ

---
