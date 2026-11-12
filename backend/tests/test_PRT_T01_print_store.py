from app.config import (
    PRINT_ALLOWED_EXTENSIONS,
    PRINT_MAX_FILE_SIZE_BYTES,
    PRINT_MAX_FILE_SIZE_MB,
    PRINT_RATE_PER_PAGE_BAHT,
)
from app.models.printing import build_seed_print_store


# T-01 (CON-FILE-01, IF-PRN-01, FR-PRT-02, FR-PRT-05) งานพื้นฐาน ไม่มี AC ตรง ๆ

def test_PRT_T01_config_matches_con_file_01_and_asm_03():
    assert set(PRINT_ALLOWED_EXTENSIONS) == {'pdf', 'docx', 'pptx', 'xlsx', 'jpg', 'png'}
    assert PRINT_MAX_FILE_SIZE_MB == 50
    assert PRINT_MAX_FILE_SIZE_BYTES == 50 * 1024 * 1024
    assert PRINT_RATE_PER_PAGE_BAHT == {'BW': 1, 'Color': 5}


def test_PRT_T01_seed_store_has_ready_printer_and_empty_spooler():
    store = build_seed_print_store()

    assert store.printers
    assert all(printer.is_ready for printer in store.printers)
    assert store.files == {}
    assert store.jobs == {}
    assert store.spooler.received_jobs == []
