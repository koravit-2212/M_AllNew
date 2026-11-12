from app.models.equipment import build_seed_equipment_store


# T-01 (FR-EQP-01, FR-EQP-02, FR-EQP-03, CON-LNS-02) งานพื้นฐาน ไม่มี AC ตรง ๆ

def test_EQP_T01_seed_has_three_equipment_types_with_counts():
    store = build_seed_equipment_store()

    names = {item.name for item in store.equipment_types.values()}
    assert names == {'ปลั๊กไฟ', 'ร่ม', 'ถุงผ้า'}
    assert all(item.available_count >= 0 for item in store.equipment_types.values())


def test_EQP_T01_seed_has_students_with_and_without_outstanding_and_empty_requests():
    store = build_seed_equipment_store()

    students = list(store.students.values())
    assert any(not student.has_outstanding for student in students)
    assert any(student.has_outstanding for student in students)
    assert store.requests == {}
    assert store.loans == []


def test_EQP_T01_each_store_is_independent():
    first = build_seed_equipment_store()
    second = build_seed_equipment_store()

    first.equipment_types['EQ-PLUG'].available_count -= 1
    first.students['64000002'].outstanding_items.clear()

    assert second.equipment_types['EQ-PLUG'].available_count == first.equipment_types['EQ-PLUG'].available_count + 1
    assert second.students['64000002'].has_outstanding
