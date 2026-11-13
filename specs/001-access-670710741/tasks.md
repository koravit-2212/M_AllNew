# แผนงานย่อย: เข้าใช้บริการห้องสมุด (Access)
- Feature: เข้าใช้บริการห้องสมุด (Access)
- Spec ID: SPEC-ACC-001
- อ้างอิง: [plan.md](./plan.md)
- วันที่: 2026-11-12

## สรุป 3 บรรทัด
- มี 5 เฟส และ 11 task ทั้งหมด
- มี 0 task ที่รอ Open Questions (Q-xx)
- เฟส 1 เป็นเฟสแรกที่เริ่มทดลองใช้งานได้จริง (AC-ACC-01: สแกน QR Code สำเร็จ)

## เฟส 0: ฐานรากสำหรับการยืนยันตัวตนและเก็บ log (ไม่มี AC)

### T-01 สร้างโครงสร้าง API และ schema สำหรับ access log
- รองรับ: FR-ACC-01, FR-ACC-03, CON-SEC-01, CON-IDN-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-04
- ไฟล์ที่แตะ: `backend/app/main.py`, `backend/app/api/access.py`, `backend/app/models/access_event.py`, `backend/app/models/facility_occupancy.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: API contract ของ `/api/access/scan`, `/api/access/status`, `/api/access/verify-manual` พร้อม schema และ route ร่างใช้งานได้
- สถานะ: เสร็จ

### T-02 สร้างข้อมูลตัวอย่างสำหรับสมาชิกและสถานะผู้ใช้บริการ
- รองรับ: FR-ACC-01, FR-ACC-02, FR-ACC-03
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-04
- ไฟล์ที่แตะ: `backend/app/services/member_profile_seed.py`, `backend/app/config.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: มีข้อมูลตัวอย่างนักศึกษา/บุคลากรที่ valid และ invalid พร้อมสถานะการเข้าใช้บริการสำหรับทดสอบ manual flow
- สถานะ: เสร็จ 

### T-03 สร้าง frontend kiosk shell และ client สำหรับเรียก API
- รองรับ: FR-ACC-01, FR-ACC-04, FR-ACC-05, CON-SEC-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-05, T-07, T-09
- ไฟล์ที่แตะ: `frontend/src/api/client.js`, `frontend/src/pages/AccessKioskPage.jsx`, `frontend/src/config.js`
- แบบหน้าจอ: UI-ACC-01 mockups/UI-ACC-01-gate-scan.html
- ต้องทำหลัง: T-01, T-02
- เสร็จเมื่อ: หน้า kiosk เปิดได้และเรียก API ของ scan flow ได้โดยใช้ client ที่ส่ง HTTPS endpoint ตาม contract
- สถานะ: เสร็จ 

#### จุดตรวจเฟส 0
- test ที่ต้องผ่านทั้งหมด: ไม่มี test เฟสเก่า; เฟสนี้เป็นโครงสร้างพื้นฐานที่ก่อนหน้าจะต้องรันได้
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-ACC-01:
  Given ระบบมีข้อมูลตัวอย่างของนักศึกษาที่ valid และ occupancy เริ่มต้น
  When เปิดหน้า kiosk และตรวจสอบว่าปุ่ม/โครงหน้าแสดงพร้อมใช้งาน
  Then ต้องเห็นหน้า scan kiosk และสามารถกดสแกน/ส่ง request ได้
- ยังขาด: ไม่มี

## เฟส 1: การยืนยันตัวตนและอนุญาตให้เข้าใช้ห้องสมุด (AC-ACC-01)

### T-04 สร้าง logic ตรวจสอบบัตร/QR และบันทึก access event สำเร็จ
- รองรับ: FR-ACC-01, FR-ACC-02, FR-ACC-03, IF-STD-01, CON-ELG-01, DOM-PRV-01
- ตรวจด้วย: AC-ACC-01
- ไฟล์ที่แตะ: `backend/app/services/access_service.py`, `backend/app/services/external_id_service.py`, `backend/app/models/access_event.py`, `backend/app/models/facility_occupancy.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-01, T-02
- เสร็จเมื่อ: เมื่อส่ง QR Code หรือรหัสบัตรที่ valid และมีสิทธิ์ ระบบบันทึก AccessEvent, อัปเดต currentOccupancy และคืนผล approved=true
- สถานะ: เสร็จ 

### T-05 สร้างหน้าจอสแกนสำเร็จและแสดงสถานะผู้ใช้บริการ
- รองรับ: FR-ACC-01, FR-ACC-03, CON-SEC-01
- ตรวจด้วย: AC-ACC-01
- ไฟล์ที่แตะ: `frontend/src/pages/AccessKioskPage.jsx`, `frontend/src/api/client.js`
- แบบหน้าจอ: UI-ACC-01 mockups/UI-ACC-01-gate-scan.html
- ต้องทำหลัง: T-03, T-04
- เสร็จเมื่อ: เมื่อสแกนบัตรสำเร็จ หน้า kiosk แสดง “ยืนยันตัวตนสำเร็จ”, ชื่อ/รหัส/เวลาเข้า และจำนวนผู้ใช้บริการในอาคารอัปเดต
- สถานะ: เสร็จ 

#### จุดตรวจเฟส 1
- test ที่ต้องผ่านทั้งหมด: T-04, T-05 และทุก test ของเฟส 0
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-ACC-01:
  Given นักศึกษามีบัตรนักศึกษาที่ถูกต้องและมีสิทธิ์เข้าใช้บริการ
  When นักศึกษาสแกน QR Code ที่เครื่องอ่าน
  Then ระบบยืนยันตัวตนสำเร็จ อนุญาตให้เข้าใช้ห้องสมุด และบันทึกข้อมูลการเข้าใช้บริการ
- ยังขาด: ไม่มี

## เฟส 2: ปฏิเสธเมื่อไม่มีสิทธิ์และบันทึกเหตุผล (AC-ACC-02)

### T-06 สร้าง logic ปฏิเสธสิทธิ์และเหตุผลแยกตามสาเหตุ รวม manual verification
- รองรับ: FR-ACC-05, FR-ACC-06, IF-STD-02, CON-ELG-01, DOM-PRV-01
- ตรวจด้วย: AC-ACC-02
- ไฟล์ที่แตะ: `backend/app/services/access_service.py`, `backend/app/services/manual_verification_service.py`, `backend/app/models/access_event.py`, `backend/app/models/manual_verification_audit.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: เมื่อสิทธิ์ไม่ผ่านหรือไม่พบข้อมูล ระบบปฏิเสธและคืน status ที่แยกเป็น "ไม่พบข้อมูล" หรือ "ไม่มีสิทธิ์" หรือ "ไม่สามารถตรวจสอบสิทธิ์ได้" พร้อมบันทึก audit log สำหรับเจ้าหน้าที่ยืนยันด้วยมือ
- สถานะ: เสร็จ 

### T-07 สร้างหน้าจอแสดงผลปฏิเสธและข้อความแนะนำให้ติดต่อเจ้าหน้าที่
- รองรับ: FR-ACC-05, FR-ACC-06
- ตรวจด้วย: AC-ACC-02
- ไฟล์ที่แตะ: `frontend/src/pages/AccessKioskPage.jsx`, `frontend/src/api/client.js`
- แบบหน้าจอ: UI-ACC-01 mockups/UI-ACC-01-gate-scan.html
- ต้องทำหลัง: T-03, T-06
- เสร็จเมื่อ: หน้า kiosk แสดงข้อความที่ชัดเจนว่าไม่มีสิทธิ์ หรือไม่พบข้อมูล และผู้ใช้ไม่สามารถเข้าได้ พร้อมข้อความให้ลองใหม่หรือติดต่อเจ้าหน้าที่
- สถานะ: เสร็จ 

#### จุดตรวจเฟส 2
- test ที่ต้องผ่านทั้งหมด: T-06, T-07 และ test ของเฟส 0-1
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-ACC-02:
  Given นักศึกษาไม่มีสิทธิ์เข้าใช้บริการ
  When นักศึกษาพยายามสแกนบัตรเพื่อเข้าห้องสมุด
  Then ระบบแจ้งเตือนและไม่อนุญาตให้เข้า
- ยังขาด: ไม่มี

## เฟส 3: อ่านข้อมูลไม่ได้และต้องไม่บันทึกการเข้าใช้บริการ (AC-ACC-03)

### T-08 สร้าง logic จัดการอ่านข้อมูลไม่ได้และยกเลิกการบันทึก
- รองรับ: FR-ACC-04, IF-STD-02
- ตรวจด้วย: AC-ACC-03
- ไฟล์ที่แตะ: `backend/app/services/access_service.py`, `backend/app/services/external_id_service.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: เมื่อระบบอ่าน QR Code หรือบัตรไม่ได้ จะคืนสถานะ "ไม่สามารถอ่านข้อมูล" และไม่สร้าง AccessEvent ใด ๆ
- สถานะ: เสร็จ 

### T-09 สร้างหน้าจอกรณีอ่านข้อมูลไม่ได้และให้สแกนใหม่
- รองรับ: FR-ACC-04, FR-ACC-05
- ตรวจด้วย: AC-ACC-03
- ไฟล์ที่แตะ: `frontend/src/pages/AccessKioskPage.jsx`, `frontend/src/api/client.js`
- แบบหน้าจอ: UI-ACC-01 mockups/UI-ACC-01-gate-scan.html
- ต้องทำหลัง: T-03, T-08
- เสร็จเมื่อ: หน้า kiosk แสดงข้อความ “ไม่สามารถอ่านข้อมูล” และให้ผู้ใช้สแกนใหม่โดยไม่มีการบันทึกการเข้าใช้บริการ
- สถานะ: เสร็จ 

#### จุดตรวจเฟส 3
- test ที่ต้องผ่านทั้งหมด: T-08, T-09 และ test ของเฟสก่อนหน้า
- เปิดระบบ: `cd backend && uvicorn app.main:app --reload` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-ACC-03:
  Given เครื่องอ่านไม่สามารถอ่าน QR Code ได้
  When นักศึกษาสแกนบัตร
  Then ระบบให้สแกนใหม่ และไม่มีการบันทึกการเข้าใช้บริการเกิดขึ้น
- ยังขาด: ไม่มี

## เฟส 4: รองรับผู้ใช้งานพร้อมกัน 500 คน และอัปเดตสถานะแบบ Real-time (AC-ACC-04)

### T-10 ปรับ backend ให้รองรับ concurrency และอัปเดต occupancy แบบ thread-safe
- รองรับ: FR-ACC-03, NFR-PRF-01, NFR-PRF-02, CON-SEC-01
- ตรวจด้วย: AC-ACC-04
- ไฟล์ที่แตะ: `backend/app/services/access_service.py`, `backend/app/models/facility_occupancy.py`, `backend/app/repositories/access_repository.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-04, T-06, T-08
- เสร็จเมื่อ: ระบบรองรับ concurrent requests 500 คนพร้อมกัน โดยการอัปเดต occupancy เป็น atomic และเวลาตอบกลับในรอบ validation/update อยู่ภายใน 2 วินาที
- สถานะ: เสร็จ 

### T-11 ทำ load test สำหรับ 500 requests พร้อมกันและตรวจสอบ latency
- รองรับ: NFR-PRF-01, NFR-PRF-02
- ตรวจด้วย: AC-ACC-04
- ไฟล์ที่แตะ: `backend/tests/test_AC_ACC_04_500_concurrent_users.py`, `backend/tests/load_test_access.py`
- แบบหน้าจอ: ไม่มี
- ต้องทำหลัง: T-10
- เสร็จเมื่อ: test_AC_ACC_04_500_concurrent_users ผ่านและผลลัพธ์ยืนยันว่า 500 request พร้อมกันยังให้บริการได้และ update occupancy ตามเวลาเงื่อนไข
- สถานะ: เสร็จ 

#### จุดตรวจเฟส 4
- test ที่ต้องผ่านทั้งหมด: T-10, T-11 และ test ของเฟสก่อนหน้า
- เปิดระบบ: `cd backend && pytest -q tests/test_AC_ACC_04_500_concurrent_users.py` และ `cd frontend && npm run dev`
- คนลองเองตาม AC-ACC-04:
  Given ผู้ใช้งานพร้อมกัน 500 คน
  When แต่ละคนสแกนเข้าใช้บริการ
  Then ระบบยังคงให้บริการได้โดยไม่ล่ม
- ยังขาด: ไม่มี

## ตารางตรวจความครบ AC
| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-ACC-01 | T-04, T-05 |
| AC-ACC-02 | T-06, T-07 |
| AC-ACC-03 | T-08, T-09 |
| AC-ACC-04 | T-10, T-11 |

## ตารางตรวจความครบ Constraint
| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| IF-STD-01 | T-04 |
| IF-STD-02 | T-06, T-08 |
| DOM-PRV-01 | T-01, T-06 |
| CON-IDN-01 | T-01, T-04 |
| CON-ELG-01 | T-04, T-06 |
| CON-SEC-01 | T-01, T-03, T-10 |
| (ไม่มี shared constraint ที่ใช้ในฟีเจอร์นี้) | - |

## ตารางตรวจความครบ FR
| FR ID | AC ที่ตรวจ FR นี้ | เฟส |
|---|---|---|
| FR-ACC-01 | AC-ACC-01 | เฟส 1 |
| FR-ACC-02 | AC-ACC-01 | เฟส 1 |
| FR-ACC-03 | AC-ACC-01 | เฟส 1 |
| FR-ACC-04 | AC-ACC-03 | เฟส 3 |
| FR-ACC-05 | AC-ACC-02 | เฟส 2 |
| FR-ACC-06 | ไม่มี AC ควรเสนอทีมเพิ่ม | เฟส 2 |

## สิ่งที่ยังไม่ทำ
- ไม่มี Open Questions ใน [spec.md](./spec.md) ปัจจุบัน จึงไม่มี task ที่ต้องรอ Q-xx
- ทุก task ที่เกี่ยวข้องกับ FR-ACC-06 ยังเป็นงานพื้นฐานที่มีผลต่อการยืนยันสิทธิ์ด้วยมือและ Audit Log แต่ยังไม่มี AC ตรงต่อใน spec
