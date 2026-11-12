from fastapi import FastAPI

from app.api.books import router as books_router
from app.api.health import router as health_router
from app.api.reservations import router as reservations_router
from app.api.search import router as search_router
from app.api.spaces import router as spaces_router

# FR-SRC-02, FR-SRC-03, FR-SRC-05, IF-CAT-01
# FastAPI app นี้ติดตั้ง route สำหรับ health probe, search, และรายละเอียดหนังสือแบบ per-copy

app = FastAPI(title='Library Search API')
app.include_router(health_router)
app.include_router(search_router)
app.include_router(books_router)
# FR-BKG-01 route ของการจองพื้นที่ (004-reserve)
app.include_router(spaces_router)
# FR-BKG-02, FR-BKG-03, FR-BKG-04 route ตรวจความว่างและบันทึกการจอง
app.include_router(reservations_router)


@app.get('/health')
def health_status() -> dict[str, str]:
    return {'status': 'ok'}
