from fastapi import APIRouter

from app.services.search_index import get_search_index_health

# FR-SRC-05, IF-CAT-01
# health route นี้ใช้สำหรับตรวจสอบสถานะ Search Index ให้ UI หรือ operator ทราบว่าระบบพร้อมใช้งานหรือไม่

router = APIRouter(prefix='/api/health')


@router.get('/search')
def read_search_health() -> dict[str, str]:
    return get_search_index_health()
