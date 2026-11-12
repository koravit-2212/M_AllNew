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
