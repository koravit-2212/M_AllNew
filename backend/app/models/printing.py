from __future__ import annotations

from dataclasses import dataclass, field

from app.config import PRINTER_READY_STATUS, PRINTER_SEED_DATA


@dataclass
class PrintFile:
    """รองรับ FR-PRT-01, FR-PRT-04: ข้อมูลไฟล์ที่ผู้ใช้เลือก (เก็บเฉพาะ metadata ไม่เก็บเนื้อไฟล์)"""

    file_id: str
    filename: str
    content_type: str
    size_bytes: int


@dataclass
class PrintJob:
    """รองรับ FR-PRT-02, FR-PRT-03: งานพิมพ์และข้อมูลการใช้บริการ"""

    printjob_id: str
    user_id: str
    file_id: str
    pages_requested: int
    copies: int
    color_mode: str
    total_cost: int
    status: str
    printer_id: str


@dataclass
class PrinterStatus:
    """รองรับ FR-PRT-05, IF-PRN-01: สถานะเครื่องพิมพ์"""

    printer_id: str
    status: str

    @property
    def is_ready(self) -> bool:
        return self.status == PRINTER_READY_STATUS


@dataclass
class FakePrintSpooler:
    """รองรับ IF-PRN-01: ตัวเชื่อม print spooler จำลอง จดงานที่ได้รับไว้แทนการส่งไปเครื่องจริง

    ใช้จนกว่าฝ่าย IT จะให้ endpoint ของ spooler จริง (ทีมเลือกเอง ไม่ได้มาจาก spec)
    """

    received_jobs: list[dict] = field(default_factory=list)

    def send(self, printer_id: str, job: PrintJob) -> None:
        self.received_jobs.append(
            {
                'printer_id': printer_id,
                'printjob_id': job.printjob_id,
                'file_id': job.file_id,
                'pages': job.pages_requested,
                'copies': job.copies,
                'color_mode': job.color_mode,
            }
        )


@dataclass
class PrintStore:
    """รองรับ FR-PRT-01 ถึง FR-PRT-05: ที่เก็บไฟล์ งานพิมพ์ และสถานะเครื่องพิมพ์ในหน่วยความจำ (แนวทางเดียวกับ 003)"""

    files: dict[str, PrintFile] = field(default_factory=dict)
    jobs: dict[str, PrintJob] = field(default_factory=dict)
    printers: list[PrinterStatus] = field(default_factory=list)
    spooler: FakePrintSpooler = field(default_factory=FakePrintSpooler)


def build_seed_print_store() -> PrintStore:
    """IF-PRN-01, FR-PRT-05: สร้างที่เก็บเริ่มต้นพร้อมเครื่องพิมพ์ตัวอย่างจาก config"""

    return PrintStore(printers=[PrinterStatus(**payload) for payload in PRINTER_SEED_DATA])
