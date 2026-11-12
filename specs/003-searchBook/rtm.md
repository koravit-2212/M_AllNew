# RTM: ค้นหาหนังสือ (Book Search)
อ้างอิง: spec.md Draft v2 | tasks.md | test-cases.md
สร้างด้วย /verify เมื่อ 2026-11-12 06:40 | test: 15 ผ่าน 0 ไม่ผ่าน

## 1. ตามรอยไปข้างหน้า (requirement ไป โค้ด ไป test)
| ID | AC | task | โค้ด (ไฟล์: ฟังก์ชัน) | test (ผล) | สถานะ |
|---|---|---|---|---|---|
| FR-SRC-01 | AC-SRC-01 | T-03, T-04, T-05 | backend/app/services/search_service.py: search_books; backend/app/api/search.py: search_books_endpoint; frontend/src/pages/SearchPage.jsx: SearchPage | backend: test_AC_SRC_01_search_api_returns_relevant_title_results_with_pagination, test_AC_SRC_01_book_seed_data.py; frontend: SearchPage.test.jsx ทั้ง 4 test ผ่าน | ครบ |
| FR-SRC-02 | AC-SRC-01, AC-SRC-04 | T-03, T-04, T-10, T-11 | backend/app/models/book.py: BookTitle.aggregated_availability; backend/app/services/book_detail_service.py: get_book_detail; frontend/src/pages/SearchPage.jsx: SearchPage; frontend/src/pages/BookDetailPage.jsx: BookDetailPage | backend + frontend tests ผ่าน; มีโค้ดแสดง aggregated availability และ per-copy detail | ครบ |
| FR-SRC-03 | AC-SRC-04 | T-10, T-11 | backend/app/services/book_detail_service.py: get_book_detail; frontend/src/pages/BookDetailPage.jsx: BookDetailPage | backend: test_AC_SRC_04_book_detail_fields; frontend: BookDetailPage.test.jsx ผ่าน | ครบ |
| FR-SRC-04 | AC-SRC-02 | T-05, T-06 | backend/app/services/search_service.py: search_books; backend/app/api/search.py: search_books_endpoint; frontend/src/pages/SearchPage.jsx: SearchPage | backend: test_AC_SRC_02_no_results.py; frontend: SearchPage.test.jsx no-result case ผ่าน | ครบ |
| FR-SRC-05 | AC-SRC-03 | T-07, T-08, T-09 | backend/app/services/search_service.py: search_books; backend/app/api/search.py: search_books_endpoint; frontend/src/pages/SearchPage.jsx: SearchPage | backend: test_AC_SRC_03_partial_results.py, test_AC_SRC_03_partial_results_and_db_unavailable.py; frontend: SearchPage.test.jsx partial + db unavailable ผ่าน | ครบ |
| NFR-USB-01 | ไม่มี AC | ไม่มี task | frontend/src/pages/SearchPage.jsx, frontend/src/pages/BookDetailPage.jsx | ไม่มี automated test ที่ตรวจ responsive/mobile experience อย่างเป็นรูปธรรม | ยังไม่ถึง |
| NFR-PRF-03 | ไม่มี AC | T-03, T-04 | backend/app/services/search_service.py: _score_book, search_books | ไม่มี load test หรือ benchmark จริง; hanya functional validation | ช่องโหว่ |
| IF-CAT-01 | ไม่มี AC | T-01, T-02, T-03, T-07, T-09, T-10 | backend/app/config.py: BOOK_SEARCH_SEED_DATA; backend/app/models/book.py: build_seed_books; backend/app/services/book_detail_service.py: get_book_detail | test ตรวจ seed data และ API ผ่าน แต่ไม่ใช้ฐานข้อมูลกลางจริง; ข้อมูลยังเป็น mock seed ใน code | ช่องโหว่ |

## 2. ตามรอยย้อนกลับ (โค้ด ไป requirement)
| โค้ด (ไฟล์: ฟังก์ชัน หรือ endpoint) | อ้าง ID | ตรงกับข้อความใน spec ไหม | หมายเหตุ |
|---|---|---|---|
| backend/app/api/search.py: search_books_endpoint | FR-SRC-01, FR-SRC-04, FR-SRC-05 | ใช่ | คืน results, message, partial, database_unavailable ตาม requirement |
| backend/app/services/search_service.py: search_books | FR-SRC-01, FR-SRC-04, FR-SRC-05 | ใช่ | fuzzy/partial match + pagination + no-result + partial-result + db-down handling ถูกทำจริง |
| backend/app/api/books.py: get_book_detail_endpoint | FR-SRC-03 | ใช่ | /api/books/{title_id} ส่งรายละเอียด per-copy ครบ |
| backend/app/services/book_detail_service.py: get_book_detail | FR-SRC-02, FR-SRC-03 | ใช่ | กำหนด title, authors, isbn, call_number, category, copies, aggregated_availability |
| frontend/src/pages/SearchPage.jsx: SearchPage | FR-SRC-01, FR-SRC-04, FR-SRC-05 | ใช่ | แสดงผล, no-result, partial-result, db unavailable ได้ตรงตาม AC |
| frontend/src/pages/BookDetailPage.jsx: BookDetailPage | FR-SRC-02, FR-SRC-03 | ใช่ | แสดงข้อมูลขั้นต่ำและ per-copy status/location ตาม mockup |
| frontend/src/api/client.js | Out of scope | ไม่ | มี getSlots / createBooking ที่ไม่เกี่ยวกับ Search Book และไม่อยู่ใน spec นี้; เป็นของแถมจาก feature อื่น |
| backend/app/config.py | IF-CAT-01 | ไม่ครบ | ข้อมูลสำคัญเป็น seed data ใน code ไม่ใช่ central library DB จริง |

## 3. ข้อค้นพบ
ชนิด: AC ไม่มี test / test อ่อน / โค้ดไม่มี FR / FR ไม่มี AC / เดา Q-xx / ละเมิด Constraint / ตัวเลขไม่ตรง spec / อ้าง ID ผิดเรื่อง
ทีมตัดสิน: แก้โค้ด / แก้ spec / เพิ่ม Q-xx / ไม่ใช่ปัญหา (พร้อมเหตุผล 1 บรรทัด)

| F-ID | ชนิด | อยู่ที่ | ขัดกับ | รายละเอียด | ทีมตัดสิน |
|---|---|---|---|---|---|
| F-001 | ละเมิด Constraint | backend/app/config.py: BOOK_SEARCH_SEED_DATA; backend/app/services/book_detail_service.py: get_book_detail | IF-CAT-01 | โค้ดใช้ seed data ภายในระบบแทน central DB จริง จึงไม่สามารถยืนยันว่าข้อมูลและสถานะตรงกับ UC-05 / UC-11 อย่างแท้จริง | ทีมตัดสิน: แก้ spec / เพิ่ม Q-xx |
| F-002 | FR ไม่มี AC | backend/app/services/search_service.py: search_books; backend/app/services/search_index.py: get_search_index_health | NFR-PRF-03 | ไม่มี load test / benchmark จริงที่ตรวจ Response Time ≤ 2–3 วินาที และ concurrency ≥ 500; ปัจจุบันเป็น functional test อย่างเดียว | ทีมตัดสิน: เพิ่ม Q-xx / ไม่ใช่ปัญหา |
| F-003 | ของแถม | frontend/src/api/client.js | Out of scope | โค้ดมี getSlots และ createBooking ที่เป็น feature อื่น ไม่เกี่ยวกับ Search Book และไม่ได้มี FR/task ใน spec นี้ | ทีมตัดสิน: ไม่ใช่ปัญหา (ถ้าแยก feature อื่น) |

## 4. แก้แล้ว
| F-ID | แก้อย่างไร | รู้ได้อย่างไร |
|---|---|---|
| ไม่มี | ไม่มีข้อค้นพบเดิมใน RTM นี้ เนื่องจากยังสร้างไฟล์ใหม่ | รัน pytest และ Vitest ทั้งหมดแล้วปรากฏผลตามรายงาน |
