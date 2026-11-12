# FR-SRC-01, FR-SRC-02, FR-SRC-03, IF-CAT-01
# ตัวเลขและกฎที่มาจาก spec จัดเก็บไว้ที่นี่เพื่อให้ reuse กับ API และ UI ต่อไป

SEARCH_PAGE_SIZE_MIN = 20
SEARCH_PAGE_SIZE_MAX = 25

BOOK_SEARCH_SEED_DATA = [
    {
        'title_id': 'bk-clean-code',
        'title': 'Clean Code',
        'authors': ['Robert C. Martin'],
        'keywords': ['clean code', 'software engineering', 'refactoring', 'clean'],
        'category': 'วิศวกรรมซอฟต์แวร์',
        'isbn': '9780132350884',
        'call_number': 'QA76.76.M37',
        'copies': [
            {'copy_id': 'CC-001', 'title_id': 'bk-clean-code', 'status': 'available', 'shelf_location': 'ชั้น 3', 'location_detail': 'โซน B'},
            {'copy_id': 'CC-002', 'title_id': 'bk-clean-code', 'status': 'borrowed', 'shelf_location': 'ชั้น 3', 'location_detail': 'โซน B'},
            {'copy_id': 'CC-003', 'title_id': 'bk-clean-code', 'status': 'available', 'shelf_location': 'ชั้น 3', 'location_detail': 'โซน B'},
        ],
    },
    {
        'title_id': 'bk-clean-architecture',
        'title': 'Clean Architecture',
        'authors': ['Robert C. Martin'],
        'keywords': ['clean architecture', 'software design', 'architecture'],
        'category': 'วิศวกรรมซอฟต์แวร์',
        'isbn': '9780134494166',
        'call_number': 'QA76.76.M37A',
        'copies': [
            {'copy_id': 'CA-001', 'title_id': 'bk-clean-architecture', 'status': 'borrowed', 'shelf_location': 'ชั้น 2', 'location_detail': 'โซน A'},
            {'copy_id': 'CA-002', 'title_id': 'bk-clean-architecture', 'status': 'borrowed', 'shelf_location': 'ชั้น 2', 'location_detail': 'โซน A'},
        ],
    },
    {
        'title_id': 'bk-thai-clean-code',
        'title': 'การเขียนโปรแกรมให้สะอาด',
        'authors': ['ผู้แต่งตัวอย่าง'],
        'keywords': ['โปรแกรม', 'การเขียนโปรแกรม', 'สะอาด', 'clean'],
        'category': 'คอมพิวเตอร์',
        'isbn': '9780000000001',
        'call_number': 'QA76.76.T5',
        'copies': [
            {'copy_id': 'TP-001', 'title_id': 'bk-thai-clean-code', 'status': 'available', 'shelf_location': 'ชั้น 4', 'location_detail': 'โซน C'},
        ],
    },
]


# ---------------------------------------------------------------------------
# 004-reserve จอง/ใช้พื้นที่ในห้องสมุด
# ---------------------------------------------------------------------------

# ASM-01 พื้นที่แต่ละประเภทมีจำนวนจำกัดและกำหนดไว้ล่วงหน้าโดยห้องสมุด
# FR-BKG-01 ข้อมูลตัวอย่างสำหรับลองระบบ (ทีมเลือกเอง ไม่ได้มาจาก spec) แทนข้อมูลจริงจากห้องสมุด
# status: 'open' = เปิดให้บริการ, 'closed' = ปิด (ไม่แสดงในรายการพื้นที่ที่ใช้งานได้)
SPACE_SEED_DATA = [
    {'space_id': 'SP-QUIET-2', 'space_type': 'โซนอ่านหนังสือ', 'facility_name': 'โซนอ่านหนังสือเงียบ ชั้น 2', 'capacity': 1, 'status': 'open'},
    {'space_id': 'SP-GROUP-1', 'space_type': 'ห้องกลุ่ม', 'facility_name': 'ห้องทำงานกลุ่ม 1', 'capacity': 1, 'status': 'open'},
    {'space_id': 'SP-COMP-1', 'space_type': 'โซนคอมพิวเตอร์', 'facility_name': 'โซนคอมพิวเตอร์ ชั้น 1', 'capacity': 1, 'status': 'open'},
    {'space_id': 'SP-MEDIA-3', 'space_type': 'ห้องสื่อ', 'facility_name': 'ห้องสื่อ ชั้น 3', 'capacity': 1, 'status': 'closed'},
]

# FR-BKG-01, FR-BKG-02 ช่วงเวลาที่เปิดให้จองของทุกพื้นที่ (ข้อมูลตัวอย่าง ทีมเลือกเอง ไม่ได้มาจาก spec)
SPACE_SLOT_TIMES = [
    ('09:00', '11:00'),
    ('11:00', '13:00'),
    ('13:00', '15:00'),
    ('15:00', '17:00'),
]

# glossary "วันเดียวกัน" เทียบด้วยเขตเวลา Asia/Bangkok
SPACE_BOOKING_TIMEZONE = 'Asia/Bangkok'
