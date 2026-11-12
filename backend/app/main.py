from fastapi import FastAPI

from app.api.books import router as books_router
from app.api.equipment import router as equipment_router
from app.api.health import router as health_router
from app.api.search import router as search_router

# FR-SRC-02, FR-SRC-03, FR-SRC-05, IF-CAT-01
# FastAPI app นี้ติดตั้ง route สำหรับ health probe, search, และรายละเอียดหนังสือแบบ per-copy
# FR-EQP-01, FR-EQP-02 route ของบริการยืมอุปกรณ์ (007-equipment)

app = FastAPI(title='Library Search API')
app.include_router(health_router)
app.include_router(search_router)
app.include_router(books_router)
app.include_router(equipment_router)


@app.get('/health')
def health_status() -> dict[str, str]:
    return {'status': 'ok'}
