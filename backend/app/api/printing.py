from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.models.printing import PrintStore, build_seed_print_store
from app.services.printing_service import (
    FileNotFound,
    InvalidColorMode,
    allowed_color_modes,
    calculate_cost,
    get_file,
    register_file,
)

# FR-PRT-01, FR-PRT-02
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
    """FR-PRT-01: รับไฟล์ที่ผู้ใช้เลือก ได้ file_id ไปใช้เลือกตัวเลือกการพิมพ์"""

    record = register_file(store, body.filename, body.content_type, body.size_bytes)
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
