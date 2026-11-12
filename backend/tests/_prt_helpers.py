# ตัวช่วยร่วมของ test จาก specs/006-printing/test-cases.md
from fastapi.testclient import TestClient

from app.api.printing import get_print_store
from app.main import app
from app.models.printing import build_seed_print_store


class PrintEnv:
    def __init__(self):
        self.store = build_seed_print_store()
        app.dependency_overrides[get_print_store] = lambda: self.store
        self.client = TestClient(app)

    def close(self):
        app.dependency_overrides.pop(get_print_store, None)

    def upload(self, filename='report.pdf', size_bytes=1_200_000):
        return self.client.post('/api/print/upload', json={'filename': filename, 'content_type': '', 'size_bytes': size_bytes})

    def options(self, file_id, pages, copies, color_mode='BW'):
        return self.client.get('/api/print/options', params={'file_id': file_id, 'pages': pages, 'copies': copies, 'color_mode': color_mode})

    def submit(self, file_id, pages, copies, color_mode='BW'):
        return self.client.post('/api/print/submit', json={'file_id': file_id, 'pages': pages, 'copies': copies, 'color_mode': color_mode})
