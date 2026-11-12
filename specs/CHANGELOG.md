# CHANGELOG ของ specs
เพิ่มรายการใหม่ไว้บนสุดเสมอ

## 004-reserve v3 (2569-11-12)
- เพิ่ม Q-01 (ผู้ใช้ตัวอย่างและประเภทผู้มีสิทธิ์ CON-ELG-01), Q-02 (ASM-02 ยังไม่ทำ), Q-03 (ASM-03/04 ยังไม่ทำ)
- AI ตัดสินแทนทีมตามคำสั่ง ไม่เปลี่ยน FR และ AC

## 001-booking v3 (2569-10-07)
- เพิ่มหมวดหน้าจอ (UI) UI-BKG-01 ถึง UI-BKG-03 และไฟล์ใน mockups/ ที่ตกลงกับ PO แล้ว
- ย้าย CON-TECH-01, DOM-PDPA-01, IF-IDP-01, IF-HIS-01, IF-NOT-01 ไป specs/000-shared/constraints.md (ข้อความและ ID เดิม) spec ฟีเจอร์เหลือแค่อ้าง ID
- เพิ่ม specs/000-shared/data-model.md และ glossary.md
- ไม่เปลี่ยน FR และ AC จึงไม่ต้องทำ CR
- plan.md หัวข้อ 4 เพิ่ม UI ID และไฟล์ mockup ของหน้าจอทั้ง 3 หน้า

## 001-booking v2 (2569-09-22)
- ผ่าน /clarify ตอบ Q-01 และเปลี่ยน CON-TECH-01 เป็น PostgreSQL
