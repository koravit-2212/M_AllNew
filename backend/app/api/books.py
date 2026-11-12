from fastapi import APIRouter, HTTPException

from app.services.book_detail_service import get_book_detail


# FR-SRC-02, FR-SRC-03, IF-CAT-01
# Route นี้ส่งข้อมูลรายละเอียดหนังสือแบบ per-copy พร้อมสถานะและตำแหน่งจัดเก็บตาม title_id

router = APIRouter(prefix='/api')


@router.get('/books/{title_id}')
def get_book_detail_endpoint(title_id: str) -> dict:
    payload = get_book_detail(title_id)
    if payload is None:
        raise HTTPException(status_code=404, detail='Book not found')
    return payload
