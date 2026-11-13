# FR-SRC-01, FR-SRC-02, FR-SRC-03, IF-CAT-01
# ตัวเลขและกฎที่มาจาก spec จัดเก็บไว้ที่นี่เพื่อให้ reuse กับ API และ UI ต่อไป

# FR-LNS-03, ASM-02: แจ้งเตือนล่วงหน้า 1–3 วันก่อนกำหนดคืน
LOAN_REMINDER_DAYS_BEFORE_DUE = (1, 3)

# FR-LNS-01, ASM-01: จำนวนหนังสือสูงสุดที่ยืมได้ต่อคน (ทีมเลือกเอง ไม่ได้มาจาก spec)
DEFAULT_MAX_BOOKS_PER_MEMBER = 2

# FR-LNS-01, FR-LNS-03: ระยะเวลายืมหนังสือเริ่มต้น (ทีมเลือกเอง ไม่ได้มาจาก spec)
LOAN_DUE_DAYS = 14

# FR-LNS-06, ASM-03: อัตราค่าปรับตามประเภทหนังสือ 3 บาท/วัน และ 20 บาท/วัน
BOOK_GENERAL_PENALTY_PER_DAY_BAHT = 3
BOOK_SPECIAL_PENALTY_PER_DAY_BAHT = 20

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

# FR-EQP-04, Q-12: เขตเวลาที่ใช้นับ "วันที่ยืม" และ due date
LIBRARY_TIMEZONE = 'Asia/Bangkok'

# FR-EQP-02, Q-11: จำนวนที่ขอยืมได้สูงสุดต่อคำขอ (ครั้งละ 1 ชิ้น)
EQUIPMENT_MAX_QUANTITY_PER_REQUEST = 1


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

# Q-05: "วันนี้" และช่วงเวลาของการจองนับตามเวลาประเทศไทย
SPACE_BOOKING_TIMEZONE = 'Asia/Bangkok'

# CON-ELG-01, Q-01: ประเภทผู้ใช้ที่มีสิทธิ์จองพื้นที่ (นักศึกษา บุคลากร ผู้ได้รับอนุญาต)
SPACE_ELIGIBLE_USER_TYPES = ('student', 'staff', 'authorized')

# CON-ELG-01, Q-01: ผู้ใช้ตัวอย่าง ชั่วคราวจนกว่าจะมีระบบยืนยันตัวตน (001/002) (ข้อมูลตัวอย่าง ทีมเลือกเอง)
SPACE_USER_SEED_DATA = [
    {'user_id': '64000001', 'name': 'นักศึกษาตัวอย่าง', 'user_type': 'student'},
    {'user_id': 'ST-1001', 'name': 'บุคลากรตัวอย่าง', 'user_type': 'staff'},
    {'user_id': 'GU-0001', 'name': 'บุคคลภายนอกตัวอย่าง', 'user_type': 'guest'},
]

# ---------------------------------------------------------------------------
# 001-access ใช้บริการเข้าใช้ห้องสมุด
# ---------------------------------------------------------------------------

# FR-ACC-01, FR-ACC-02, CON-ELG-01, DOM-PRV-01
# ข้อมูลสมาชิกตัวอย่างสำหรับการยืนยันตัวตนและตรวจสิทธิ์
# member_id ใช้ติดตามการเข้า/ออกและ manual verification โดยไม่เก็บข้อมูลบัตรประชาชนแบบละเอียด
ACCESS_CONCURRENT_REQUEST_LIMIT = 500
ACCESS_VALIDATION_TARGET_SECONDS = 2

ACCESS_MEMBER_SEED_DATA = [
    {
        'member_id': 'STD-1001',
        'member_type': 'student',
        'name': 'นักศึกษาตัวอย่าง ก',
        'eligibility_status': 'eligible',
        'status': 'active',
        'last_verified_at': '2026-11-12T08:30:00+00:00',
    },
    {
        'member_id': 'STF-2001',
        'member_type': 'staff',
        'name': 'บุคลากรตัวอย่าง',
        'eligibility_status': 'eligible',
        'status': 'active',
        'last_verified_at': '2026-11-12T08:30:00+00:00',
    },
    {
        'member_id': 'STD-1002',
        'member_type': 'student',
        'name': 'นักศึกษาตัวอย่าง ข',
        'eligibility_status': 'ineligible',
        'status': 'inactive',
        'last_verified_at': None,
    },
    {
        'member_id': 'UNKNOWN-999',
        'member_type': 'unknown',
        'name': 'ไม่พบข้อมูล',
        'eligibility_status': 'not_found',
        'status': 'unverified',
        'last_verified_at': None,
    },
    {
        'member_id': 'STD-1003',
        'member_type': 'student',
        'name': 'นักศึกษาตัวอย่าง ค',
        'eligibility_status': 'verification_failed',
        'status': 'active',
        'last_verified_at': None,
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
