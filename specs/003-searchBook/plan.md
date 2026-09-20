# specs/003-searchBook/plan.md

1. สรุปแนวทาง (5 บรรทัด)
- ฟีเจอร์นี้ให้ผู้ใช้ (นักศึกษา/บุคลากร) ค้นหาหนังสือด้วยคำค้น (title/author/keywords/ISBN) และเห็นรายการผลลัพธ์พร้อมสถานะสรุปและหน้ารายละเอียดแบบ per-copy
- แนวทางการสร้าง: ทำ Search API ที่ใช้ดัชนีสำหรับการค้นหาแบบ fuzzy/partial match และอ่านสถานะจริงจากฐานข้อมูลกลางตาม IF-CAT-01 เพื่อความถูกต้อง
- ผลลัพธ์ในหน้ารายการเป็น aggregated per-title (แสดง availability สรุป) และหน้ารายละเอียดแสดงสำเนาแต่ละเล่มพร้อมตำแหน่ง (per-copy)
- รองรับ pagination 20–25 ต่อหน้า, เรียงตาม relevance, และคืน partial results พร้อมแจ้งเตือนเมื่อ DB ช้า
- ให้คำนึงเรื่อง performance (NFR-PRF-03: 2–3 วินาที, concurrency ≥ 500)

2. เทคโนโลยีที่ใช้
สิ่งที่เลือก | มาจาก | หมายเหตุ
---|---|---
Frontend: React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ UI บนคอมพิวเตอร์และมือถือ (สอดคล้อง NFR-USB-01)
Backend: Python (FastAPI) | ทีมเลือกเอง ไม่ได้มาจาก spec | เบื้องต้นเป็นเทมเพลตทีมวิชา
Central Library DB (existing) | IF-CAT-01 | ฐานข้อมูลกลางที่เป็นแหล่งอ้างอิงสถานะยืม-คืน (authoritative)
Search index: Elasticsearch (or managed search) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้เพื่อรองรับ fuzzy/partial match และ relevance ranking; ต้องมีกระบวนการ sync กับ Central DB
Cache: Redis (optional) | ทีมเลือกเอง ไม่ได้มาจาก spec | แคชผลลัพธ์หรือ metadata ช่วยลด latency
Task queue: Celery / Cron jobs | ทีมเลือกเอง ไม่ได้มาจาก spec | สำหรับงาน sync ดัชนีจาก Central DB

3. โมเดลข้อมูล (สรุปหลัก)
- BookTitle
  - id (title_id) — รองรับ FR-SRC-01, FR-SRC-02, FR-SRC-03
  - title, authors[], keywords[], category, isbn, call_number
  - aggregated_availability (computed) — สรุปสถานะจาก BookCopy
- BookCopy
  - copy_id (barcode), title_id, status (available/borrowed/reserved), shelf_location, location_detail
  - รองรับ FR-SRC-02, FR-SRC-03 (per-copy status)
- SearchIndex (ภายนอก/Elasticsearch)
  - index documents derived from BookTitle + denormalized availability metadata (but authoritative status read from Central DB on detail view)
  - รองรับ FR-SRC-01 (fuzzy/partial match) และ relevance

ข้อสังเกตเรื่องข้อมูล: ตาม IF-CAT-01 ให้ใช้ Central DB เป็นแหล่งอ้างอิงสถานะจริง — ห้ามทำ authoritative write ในระบบค้นหา

4. API / หน้าจอ
- GET /api/search?q={q}&page={n}&per_page={m}
  - input: q, page, per_page, sort
  - output: list of title-level results [{title_id, title, authors, snippet, aggregated_availability, relevance_score}] , total, partial (bool)
  - รองรับ: FR-SRC-01, FR-SRC-02, NFR-PRF-03, AC-SRC-01
- GET /api/books/{title_id}
  - input: title_id
  - output: {title, authors, isbn, call_number, category, copies: [{copy_id, status, shelf_location}], metadata}
  - ดึงสถานะ per-copy จาก Central DB (on-demand) เพื่อให้ข้อมูลเป็น authoritative — รองรับ FR-SRC-03, FR-SRC-02, AC-SRC-04
- GET /api/health/search
  - output: index_status, last_sync_time, sync_health
  - ใช้สำหรับตรวจสอบและ debug

หน้าจอ (UI)
- Search Page (desktop/mobile)
  - กล่องค้นหา, ตัวกรองพื้นฐาน, ผลลัพธ์แบบรายการ (20–25 ต่อหน้า), แสดง aggregated availability, ป้ายแจ้งเตือน partial results
  - รองรับ AC-SRC-01, AC-SRC-02
- Book Detail Page
  - แสดงฟิลด์ขั้นต่ำ (ชื่อ, ผู้แต่ง, เลขเรียก/ISBN, หมวดหมู่, รายการสำเนาพร้อมสถานะและตำแหน่ง)
  - รองรับ AC-SRC-04

5. ตารางตรวจ Constraints
Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ
---|---|---
IF-CAT-01 | อ่านสถานะ per-copy จาก Central Library DB ใน API `GET /api/books/{title_id}` และใช้ sync job เพื่ออัปเดต SearchIndex | ใช้แล้ว

(ไม่มี CON/DOM อื่นใน spec)

6. แผนทดสอบจาก Acceptance Criteria
AC ID | ชื่อ test | ทดสอบอย่างไร
---|---|---
AC-SRC-01 | test_AC_SRC_01_performance_and_relevance | เตรียมฐานข้อมูลตัวอย่างรวมหนังสือที่ตรงกับคำค้นจริง รัน `GET /api/search` วัด response time (ต้อง ≤ 2–3s) และตรวจสอบว่าอันดับผลลัพธ์มีรายการที่คาดหวัง; ทดสอบภายใต้โหลดจำลอง (n users) เพื่อยืนยัน concurrency ≥ 500 (ในสภาพแวดล้อม CI อาจต้องใช้เครื่องมือ load test)
AC-SRC-02 | test_AC_SRC_02_no_results | รัน `GET /api/search?q=<nonexistent>` และตรวจสอบข้อความว่า "ไม่พบข้อมูลหนังสือ"
AC-SRC-03 | test_AC_SRC_03_partial_results_and_db_unavailable | จำลองกรณี Central DB ตอบช้า/ให้ผลบางส่วน: ให้ SearchIndex คืนผลที่มีและ response มี `partial=true` และแสดงข้อความแจ้ง; ถ้า Central DB ปิดจริง ให้ API ตอบด้วยข้อความว่า "ฐานข้อมูลหนังสือไม่พร้อมใช้งาน"
AC-SRC-04 | test_AC_SRC_04_book_detail_fields | เปิด `GET /api/books/{title_id}` และตรวจสอบว่าคืนค่าอย่างน้อย: ชื่อ, ผู้แต่ง, เลขเรียก/ISBN, หมวดหมู่, สถานะยืม-คืนของสำเนา และตำแหน่งจัดเก็บ

7. ลำดับงาน (งานย่อย 7 ขั้น)
1. เตรียมสเปคการเชื่อมต่อ Central DB และตัวอย่างข้อมูล (FR-SRC-01, IF-CAT-01)
2. ตั้งค่า Search index (Elasticsearch) และออกแบบ mapping สำหรับ fuzzy/relevance (FR-SRC-01)
3. พัฒนา API `GET /api/search` ใช้ index เป็นหลักและรองรับ pagination, relevance (FR-SRC-01, AC-SRC-01)
4. พัฒนา sync job (ETL) เพื่อดึงข้อมูลจาก Central DB มาสร้าง/อัปเดต SearchIndex (IF-CAT-01)
5. พัฒนา API `GET /api/books/{title_id}` โดยดึงสถานะ per-copy จาก Central DB (FR-SRC-03, AC-SRC-04)
6. พัฒนา UI Search Page และ Book Detail Page พร้อมแสดง partial-results indicator (AC-SRC-01, AC-SRC-04)
7. ทดสอบ performance และ load testing, ปรับ caching/scale ตาม NFR-PRF-03 (AC-SRC-01)

8. สิ่งที่ยังไม่ทำ (Open Questions)
- ขณะนี้ใน `spec.md` ไม่มี Open Questions คงค้าง — ทุกคำถามหลักถูกตัดสินเป็น ASM-xx แล้ว


---

**สรุปสั้น ๆ ตามข้อที่ต้องรายงาน:**
1) Constraint ที่ยังไม่ได้ใช้: ไม่มี (IF-CAT-01 ถูกนำไปใช้)
2) AC ที่ทดสอบยาก: `AC-SRC-01` (ทดสอบ concurrency ≥500 และ Response Time ≤2–3s ต้องใช้เครื่องมือ load test และสภาพแวดล้อมที่มีทรัพยากร) และบางส่วนของ `AC-SRC-03` (การจำลอง partial DB responses/ความล้มเหลวของ DB)
3) สิ่งที่อยากเดาแต่ไม่ได้เดา: โซลูชันการเลือก Search engine (Elasticsearch vs DB FTS), นโยบาย sync frequency และ TTL ของ cache — ต้องการการตัดสินใจจากทีม/IT
