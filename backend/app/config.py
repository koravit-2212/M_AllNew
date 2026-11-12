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
# 007-equipment ใช้บริการยืมอุปกรณ์
# ---------------------------------------------------------------------------

# FR-EQP-01, FR-EQP-02 ประเภทอุปกรณ์ (ปลั๊กไฟ ร่ม ถุงผ้า) พร้อมจำนวนคงเหลือตัวอย่าง
# จำนวนคงเหลือเป็นข้อมูลตัวอย่างสำหรับลองระบบ (ทีมเลือกเอง ไม่ได้มาจาก spec)
EQUIPMENT_SEED_DATA = [
    {'equipment_type_id': 'EQ-PLUG', 'name': 'ปลั๊กไฟ', 'available_count': 4},
    {'equipment_type_id': 'EQ-UMBRELLA', 'name': 'ร่ม', 'available_count': 2},
    {'equipment_type_id': 'EQ-BAG', 'name': 'ถุงผ้า', 'available_count': 5},
]

# FR-EQP-03, FR-EQP-06, CON-LNS-02 นักศึกษาตัวอย่างและรายการค้างคืน
# ข้อมูลจริงควรมาจาก 005-borrow-return ซึ่งยังไม่มี (ทีมเลือกเอง ไม่ได้มาจาก spec)
EQUIPMENT_STUDENT_SEED_DATA = [
    {'student_id': '64000001', 'name': 'นักศึกษาตัวอย่าง ก', 'outstanding_items': []},
    {'student_id': '64000002', 'name': 'นักศึกษาตัวอย่าง ข', 'outstanding_items': [{'item': 'ร่ม', 'days_overdue': 2}]},
]

# FR-EQP-04, ASM-03, Q-03: จำนวนวันที่ยืมได้ของแต่ละประเภท นับจากวันที่ยืม (ทีมตอบ: ทุกประเภท 1 วัน)
EQUIPMENT_LOAN_DAYS = {
    'EQ-PLUG': 1,
    'EQ-UMBRELLA': 1,
    'EQ-BAG': 1,
}

# FR-EQP-04: เขตเวลาที่ใช้นับ "วันที่ยืม" ตาม glossary (วันเดียวกัน = Asia/Bangkok)
LIBRARY_TIMEZONE = 'Asia/Bangkok'
