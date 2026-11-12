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
# 006-printing ใช้บริการปริ้นเอกสาร
# ---------------------------------------------------------------------------

# CON-FILE-01, ASM-02 รองรับเฉพาะ PDF, DOCX, PPTX, XLSX, JPG, PNG
PRINT_ALLOWED_EXTENSIONS = ('pdf', 'docx', 'pptx', 'xlsx', 'jpg', 'png')

# CON-FILE-01, ASM-02 ขนาดไฟล์ไม่เกิน 50 MB ต่อไฟล์
PRINT_MAX_FILE_SIZE_MB = 50
PRINT_MAX_FILE_SIZE_BYTES = PRINT_MAX_FILE_SIZE_MB * 1024 * 1024

# FR-PRT-02, ASM-01, ASM-03 อัตราค่าพิมพ์ต่อหน้า (บาท): ขาว-ดำ 1 บาท สี 5 บาท
PRINT_RATE_PER_PAGE_BAHT = {
    'BW': 1,
    'Color': 5,
}

# FR-PRT-05, IF-PRN-01 เครื่องพิมพ์ตัวอย่าง (ทีมเลือกเอง ไม่ได้มาจาก spec)
# status: 'ready' = พร้อมใช้งาน, 'offline' / 'error' = ไม่พร้อมใช้งาน
PRINTER_SEED_DATA = [
    {'printer_id': 'PRN-LIB-01', 'status': 'ready'},
]
PRINTER_READY_STATUS = 'ready'
