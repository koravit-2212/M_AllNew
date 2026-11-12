from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.config import PRINT_ALLOWED_EXTENSIONS, PRINT_MAX_FILE_SIZE_MB
from app.models.printing import PrintStore, build_seed_print_store
from app.services.printing_service import (
    FileNotFound,
    InvalidColorMode,
    PrinterNotReady,
    UnsupportedFile,
    allowed_color_modes,
    calculate_cost,
    get_file,
    job_payload,
    printers_status,
    register_file,
    submit_print_job,
)

# FR-PRT-01, FR-PRT-02, FR-PRT-03, IF-PRN-01
# Route ของบริการปริ้นเอกสาร เก็บข้อมูลในหน่วยความจำแบบเดียวกับ 003 (ทีมเลือกเอง ไม่ได้มาจาก spec)

router = APIRouter(prefix='/api')

_store = build_seed_print_store()


def get_print_store() -> PrintStore:
    """ที่เก็บงานพิมพ์ที่ใช้ร่วมทุก route (test แทนที่ได้ด้วย dependency_overrides)"""

    return _store


class UploadIn(BaseModel):
    # Q-07: ส่งเฉพาะข้อมูลไฟล์ ไม่ส่งเนื้อไฟล์
    filename: str = Field(min_length=1)
    content_type: str = ''
    size_bytes: int = Field(ge=0)


@router.post('/print/upload', status_code=201)
def upload_file(body: UploadIn, store: PrintStore = Depends(get_print_store)) -> dict:
    """FR-PRT-01: รับไฟล์ที่ผู้ใช้เลือก ได้ file_id ไปใช้เลือกตัวเลือกการพิมพ์
    FR-PRT-04: ไฟล์ไม่รองรับ ตอบ 415 และไม่ได้ file_id
    """

    try:
        record = register_file(store, body.filename, body.content_type, body.size_bytes)
    except UnsupportedFile:
        # FR-PRT-04, CON-FILE-01: แจ้งเตือนพร้อมชนิดและขนาดที่รองรับ (ค่าจาก config)
        raise HTTPException(
            status_code=415,
            detail={
                'message': 'ไม่รองรับไฟล์ชนิดนี้',
                'allowed_extensions': list(PRINT_ALLOWED_EXTENSIONS),
                'max_size_mb': PRINT_MAX_FILE_SIZE_MB,
            },
        )
    # Q-05: ระบบไม่นับหน้าจากไฟล์ ผู้ใช้กรอกเอง
    return {'file_id': record.file_id, 'filename': record.filename, 'size_bytes': record.size_bytes, 'pages_detected': None}


@router.get('/print/options')
def print_options(
    file_id: str,
    pages: int = Query(..., ge=1),
    copies: int = Query(..., ge=1),
    color_mode: str = 'BW',
    store: PrintStore = Depends(get_print_store),
) -> dict:
    """FR-PRT-01, FR-PRT-02: ตัวเลือกการพิมพ์และค่าใช้บริการที่คำนวณแล้วก่อนให้ยืนยัน"""

    try:
        get_file(store, file_id)
        cost = calculate_cost(pages, copies, color_mode)
    except FileNotFound:
        raise HTTPException(status_code=404, detail='File not found')
    except InvalidColorMode:
        raise HTTPException(status_code=422, detail='Invalid color mode')
    return {
        'file_id': file_id,
        'pages': pages,
        'copies': copies,
        'color_mode': color_mode,
        'allowed_color_modes': allowed_color_modes(),
        **cost,
    }


class SubmitIn(BaseModel):
    file_id: str
    pages: int = Field(ge=1)
    copies: int = Field(ge=1)
    color_mode: str = 'BW'


@router.post('/print/submit', status_code=201)
def submit_print(body: SubmitIn, store: PrintStore = Depends(get_print_store)) -> dict:
    """FR-PRT-03, IF-PRN-01: ยืนยันการพิมพ์ ส่งงานไป spooler และบันทึกการใช้บริการ
    FR-PRT-05: เครื่องพิมพ์ไม่พร้อม ตอบ 409 "เครื่องพิมพ์ไม่พร้อมใช้งาน" และไม่ส่งงาน
    """

    try:
        job = submit_print_job(store, body.file_id, body.pages, body.copies, body.color_mode)
    except FileNotFound:
        raise HTTPException(status_code=404, detail='File not found')
    except InvalidColorMode:
        raise HTTPException(status_code=422, detail='Invalid color mode')
    except PrinterNotReady:
        raise HTTPException(status_code=409, detail='เครื่องพิมพ์ไม่พร้อมใช้งาน')
    return job_payload(store, job)


@router.get('/print/jobs/{printjob_id}')
def get_print_job(printjob_id: str, store: PrintStore = Depends(get_print_store)) -> dict:
    """FR-PRT-03: อ่านงานพิมพ์ที่บันทึกไว้"""

    job = store.jobs.get(printjob_id)
    if job is None:
        raise HTTPException(status_code=404, detail='Print job not found')
    return job_payload(store, job)


@router.get('/printers/status')
def get_printers_status(store: PrintStore = Depends(get_print_store)) -> dict:
    """FR-PRT-05, IF-PRN-01: สถานะเครื่องพิมพ์"""

    return {'printers': printers_status(store)}
