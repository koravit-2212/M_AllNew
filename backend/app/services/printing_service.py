from __future__ import annotations

from app.config import PRINT_RATE_PER_PAGE_BAHT
from app.models.printing import PrintFile, PrintJob, PrintStore

# FR-PRT-01, FR-PRT-02, FR-PRT-03, IF-PRN-01
# กฎของบริการปริ้นเอกสาร แยกจาก route เพื่อให้ test เรียกได้ตรง ๆ

# ชื่อชนิดการพิมพ์ที่แสดงบนหน้าจอ (ข้อความจาก UI-PRT-01) อัตราอยู่ใน config (ASM-03)
COLOR_MODE_LABELS = {'BW': 'ขาว-ดำ', 'Color': 'สี'}


class FileNotFound(Exception):
    """ไม่พบไฟล์ที่เลือก"""


class InvalidColorMode(Exception):
    """ชนิดการพิมพ์ไม่อยู่ในตัวเลือก"""


def register_file(store: PrintStore, filename: str, content_type: str, size_bytes: int) -> PrintFile:
    """FR-PRT-01, Q-07: บันทึกข้อมูลไฟล์ที่ผู้ใช้เลือก (ไม่เก็บเนื้อไฟล์)"""

    file_id = f'FILE-{len(store.files) + 1:04d}'
    record = PrintFile(file_id=file_id, filename=filename, content_type=content_type, size_bytes=size_bytes)
    store.files[file_id] = record
    return record


def allowed_color_modes() -> list[dict]:
    """FR-PRT-01: ตัวเลือกชนิดการพิมพ์ พร้อมอัตราต่อหน้า (ASM-01, ASM-03)"""

    return [{'code': code, 'label': COLOR_MODE_LABELS.get(code, code), 'rate_per_page': rate} for code, rate in PRINT_RATE_PER_PAGE_BAHT.items()]


def calculate_cost(pages: int, copies: int, color_mode: str) -> dict:
    """FR-PRT-02, ASM-01, ASM-03: ค่าใช้บริการ = จำนวนหน้า × จำนวนชุด × อัตราต่อหน้าของชนิดการพิมพ์"""

    if color_mode not in PRINT_RATE_PER_PAGE_BAHT:
        raise InvalidColorMode(color_mode)
    total_pages = pages * copies
    return {'total_pages': total_pages, 'estimated_cost': total_pages * PRINT_RATE_PER_PAGE_BAHT[color_mode]}


def get_file(store: PrintStore, file_id: str) -> PrintFile:
    record = store.files.get(file_id)
    if record is None:
        raise FileNotFound(file_id)
    return record


def ready_printer(store: PrintStore):
    """FR-PRT-05, IF-PRN-01: เครื่องพิมพ์ตัวแรกที่พร้อมใช้งาน (ไม่มีคืน None)"""

    return next((printer for printer in store.printers if printer.is_ready), None)


def submit_print_job(store: PrintStore, file_id: str, pages: int, copies: int, color_mode: str, user_id: str = '') -> PrintJob:
    """FR-PRT-03, IF-PRN-01: ส่งงานไปยังเครื่องปริ้นผ่าน spooler และบันทึกข้อมูลการใช้บริการ
    Q-08: ยังไม่มีล็อกอิน user_id เป็นค่าว่าง
    """

    get_file(store, file_id)
    cost = calculate_cost(pages, copies, color_mode)
    printer = ready_printer(store)
    job = PrintJob(
        printjob_id=f'JOB-{len(store.jobs) + 1:04d}',
        user_id=user_id,
        file_id=file_id,
        pages_requested=pages,
        copies=copies,
        color_mode=color_mode,
        total_cost=cost['estimated_cost'],
        status='sent',
        printer_id=printer.printer_id if printer else '',
    )
    store.spooler.send(job.printer_id, job)
    store.jobs[job.printjob_id] = job
    return job


def job_payload(store: PrintStore, job: PrintJob) -> dict:
    """FR-PRT-03: ข้อมูลงานพิมพ์ที่บันทึกไว้"""

    record = store.files.get(job.file_id)
    return {
        'printjob_id': job.printjob_id,
        'status': job.status,
        'file_id': job.file_id,
        'filename': record.filename if record else '',
        'pages': job.pages_requested,
        'copies': job.copies,
        'total_pages': job.pages_requested * job.copies,
        'color_mode': job.color_mode,
        'total_cost': job.total_cost,
        'printer_id': job.printer_id,
    }
