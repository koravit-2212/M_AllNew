from fastapi import APIRouter, Query

from app.config import SEARCH_PAGE_SIZE_MIN
from app.services.search_service import search_books


# FR-SRC-01, FR-SRC-02, NFR-PRF-03, IF-CAT-01
# Route นี้ใช้สำหรับค้นหาหนังสือระดับ title พร้อม relevance, pagination, และ aggregated availability

router = APIRouter(prefix='/api')


@router.get('/search')
def search_books_endpoint(
    q: str = Query('', description='คำค้นหนังสือ'),
    page: int = Query(1, ge=1, description='หมายเลขหน้า'),
    per_page: int = Query(SEARCH_PAGE_SIZE_MIN, ge=SEARCH_PAGE_SIZE_MIN, le=25, description='จำนวนผลลัพธ์ต่อหน้า'),
    partial: bool = Query(False, description='ระบุว่าผลลัพธ์เป็นบางส่วนจากฐานข้อมูลที่ตอบช้า'),
    database_unavailable: bool = Query(False, description='ระบุว่าฐานข้อมูลหนังสือไม่พร้อมใช้งาน'),
) -> dict:
    payload = search_books(
        query=q,
        page=page,
        per_page=per_page,
        partial=partial,
        database_unavailable=database_unavailable,
    )
    if not payload.get('results') and not partial and not database_unavailable:
        payload['message'] = 'ไม่พบข้อมูลหนังสือ'
    return payload
