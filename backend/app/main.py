from fastapi import FastAPI

from app.api.books import router as books_router
from app.api.health import router as health_router
from app.api.printing import router as printing_router
from app.api.search import router as search_router

# FR-SRC-02, FR-SRC-03, FR-SRC-05, IF-CAT-01
# FastAPI app นี้ติดตั้ง route สำหรับ health probe, search, และรายละเอียดหนังสือแบบ per-copy

app = FastAPI(title='Library Search API')
app.include_router(health_router)
app.include_router(search_router)
app.include_router(books_router)
# FR-PRT-01 ถึง FR-PRT-05 route ของบริการปริ้นเอกสาร (006-printing)
app.include_router(printing_router)


@app.get('/health')
def health_status() -> dict[str, str]:
    return {'status': 'ok'}
