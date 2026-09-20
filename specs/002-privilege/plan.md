# แผนงาน: ตรวจสอบสิทธิ์การเข้าใช้บริการ (Access Verification)

## 1. สรุปแนวทาง
- ฟีเจอร์นี้ทำหน้าที่รับข้อมูลผู้ใช้จาก UC-01 แล้วตรวจสอบสิทธิ์ผ่านระบบบัตรนักศึกษาเพื่อกำหนดว่าให้เข้าใช้บริการได้หรือไม่ตามสถานะ ปกติ / ถูกระงับสิทธิ์ / ไม่พบข้อมูล
- ผู้ใช้หลักคือ นักศึกษา บุคลากร หรือผู้ที่ห้องสมุด/มหาวิทยาลัยกำหนดให้สามารถใช้บริการได้ และเจ้าหน้าที่ห้องสมุดที่ต้องทำ Manual Verification
- แนวทางคือสร้างส่วนรับข้อมูลและส่งต่อไปยังระบบบัตรนักศึกษาแบบ synchronous โดยใช้ timeout 5 วินาที และจัดการผลตอบกลับให้สอดคล้องกับข้อความที่สั้น กระชับ และสื่อความหมายตรง
- ระบบจะคืนผลให้อยู่ในรูปแบบที่ UC-01 สามารถตัดสินใจอนุญาต/ปฏิเสธได้ทันที และจัดการกรณี timeout หรือไม่พบข้อมูลด้วยข้อความและการปฏิเสธอัตโนมัติ
- สำหรับกรณี Manual Verification จะใช้กระบวนการแยกต่างหากที่ต้องมีเจ้าหน้าที่รับสิทธิ์เพียงคนเดียวและบันทึก Audit Log เสมอ

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ UI ตรวจสอบสิทธิ์และแสดงผลสถานะต่อผู้ใช้ |
| Python FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ API และประสานกับระบบบัตรนักศึกษา |
| HTTPS transport สำหรับเรียก API ภายนอก | IF-STD-01, CON-SEC-01 | ต้องเรียกผ่าน HTTPS เท่านั้น |
| Client สำหรับเรียกระบบบัตรนักศึกษา | IF-STD-01 | จัดการ timeout 5 วินาที และ error handling |
| Backend storage สำหรับ Audit Log | ASM-06 | บันทึกผู้ดำเนินการ วันเวลา เหตุผล และผลการยืนยัน |

## 3. โมเดลข้อมูล

| Entity | ฟิลด์หลัก | รองรับ FR/ASM |
|---|---|---|
| VerificationRequest | requestId, userIdentifier, cardData, qrCodeData, sourceSystem, requestedAt, sessionId | FR-AVR-01 |
| VerificationResult | requestId, userIdentifier, status, statusMessage, decision, timeoutFlag, verifiedAt | FR-AVR-02, FR-AVR-03, FR-AVR-04 |
| UserEligibilityRecord | userIdentifier, userType, eligibilityStatus, membershipSource, lastUpdatedAt | CON-ELG-01, CON-IDN-01 |
| ManualVerificationRecord | requestId, actorId, actorRole, reason, approvalDecision, approvedAt, auditReference | FR-AVR-04, ASM-05, ASM-06 |
| AuditLogEntry | logId, entityType, actorId, actorRole, timestamp, action, reason, outcome | ASM-06 |

หมายเหตุ:
- โมเดลจะเก็บเฉพาะข้อมูลที่จำเป็นเพื่อระบุตัวตนและตรวจสอบสิทธิ์ตาม CON-IDN-01 และ CON-ELG-01 เท่านั้น
- ไม่มีฟิลด์ใดที่เก็บข้อมูลที่ไม่จำเป็นหรือขัดกับข้อจำกัดใน spec เช่น ไม่มีการจัดเก็บข้อมูลที่ไม่เกี่ยวกับการยืนยันสิทธิ์หรือ Manual Verification

## 4. API / หน้าจอ

- POST /api/access-verification/verify
  - Input: userIdentifier, cardData, qrCodeData, requestSource
  - Output: verificationStatus, statusMessage, decision, timeoutFlag, verifiedAt
  - รองรับ: FR-AVR-01, FR-AVR-02, FR-AVR-03

- POST /api/access-verification/manual-verify
  - Input: requestId, actorId, actorRole, reason, approvalDecision
  - Output: verificationOutcome, auditReference
  - รองรับ: FR-AVR-04, ASM-05, ASM-06

- GET /api/access-verification/status/{requestId}
  - Input: requestId
  - Output: latest verification status and message
  - รองรับ: FR-AVR-02, FR-AVR-03, FR-AVR-04

- หน้า: ตรวจสอบสิทธิ์เข้าใช้บริการ
  - Input: สแกนบัตร/QR หรือข้อมูลประจำตัวผู้ใช้
  - Output: แสดงข้อความสั้น เช่น “ยืนยันสิทธิ์สำเร็จ”, “สิทธิ์ถูกระงับ”, “ไม่พบข้อมูลผู้ใช้”, “ลองใหม่ภายหลัง”
  - รองรับ: FR-AVR-01, FR-AVR-02, FR-AVR-03, FR-AVR-04, AC-AVR-01 ถึง AC-AVR-03

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| IF-STD-01 | เรียก API ภายนอกผ่าน client ใน FastAPI และใช้ timeout 5 วินาที, รวมทั้งจัดการ error state | ใชแล้ว |
| CON-ELG-01 | ตรวจสอบประเภทผู้ใช้ใน UserEligibilityRecord ว่าเป็นนักศึกษา/บุคลากร/ได้รับอนุญาต | ใชแล้ว |
| CON-IDN-01 | ใช้บัตรนักศึกษาหรือ QR Code เป็นข้อมูลยืนยันตัวตนก่อนส่งให้ระบบตรวจสอบ | ใชแล้ว |
| CON-SEC-01 | กำหนดว่าทุกการเชื่อมต่อระหว่างระบบและระบบบัตรนักศึกษาทั้งหมดต้องใช้ HTTPS | ใชแล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-AVR-01 | test_AC_AVR_01_valid_access_status_mapping | ตรวจสอบว่าหากข้อมูลผู้ใช้ถูกต้อง ระบบส่ง request ไปยังระบบบัตรนักศึกษา และคืนผลตามสถานะที่ถูกต้อง เช่น “ยืนยันสิทธิ์สำเร็จ”, “สิทธิ์ถูกระงับ”, “ไม่พบข้อมูลผู้ใช้” |
| AC-AVR-02 | test_AC_AVR_02_external_timeout_failure | จำลองระบบบัตรนักศึกษาไม่ตอบหรือ timeout มากกว่า 5 วินาที แล้วตรวจสอบว่าระบบแสดง “ลองใหม่ภายหลัง” และถือว่าการตรวจสอบล้มเหลว |
| AC-AVR-03 | test_AC_AVR_03_missing_user_denied_access | จำลองกรณีไม่พบข้อมูลผู้ใช้ในระบบบัตรนักศึกษา แล้วตรวจสอบว่าระบบแสดง “ไม่พบข้อมูลผู้ใช้” และปฏิเสธการเข้าใช้บริการโดยอัตโนมัติ |

## 7. ลำดับงาน

1. กำหนดสัญญาการตรวจสอบสิทธิ์และ mapping สถานะผลลัพธ์ (FR-AVR-01, FR-AVR-02, AC-AVR-01)
2. สร้าง client สำหรับเรียกระบบบัตรนักศึกษาใน FastAPI พร้อม timeout 5 วินาที และความผิดพลาดแบบ fail-safe (FR-AVR-01, FR-AVR-03, AC-AVR-02)
3. Implement การแปลงผลตอบกลับจากระบบภายนอกเป็นข้อความสั้นและสื่อความหมายตรงกับสถานะ (FR-AVR-02, AC-AVR-01)
4. Implement flow เมื่อไม่พบข้อมูลผู้ใช้ ให้แสดง “ไม่พบข้อมูลผู้ใช้” และปฏิเสธเข้าใช้งานโดยอัตโนมัติ (FR-AVR-04, AC-AVR-03)
5. สร้างกระบวนการ Manual Verification สำหรับเจ้าหน้าที่ที่ได้รับสิทธิ์ เพื่อยืนยันแทนระบบและบันทึก Audit Log (FR-AVR-04, ASM-05, ASM-06)
6. สร้างหน้าจอและการเชื่อมต่อ API สำหรับ UI ตรวจสอบสิทธิ์ (FR-AVR-01, FR-AVR-02, FR-AVR-03, FR-AVR-04)
7. ทดสอบตาม AC-AVR-01 ถึง AC-AVR-03 และตรวจสอบเงื่อนไข Constraints ทั้งหมด
8. Review final กับทีมและตรวจสอบความครอบคลุมต่อ spec ก่อนดำเนินการต่อในขั้น plan หรือ development

## 8. สิ่งที่ยังไม่ทำ
- ไม่มี Open Questions ค้างใน spec ปัจจุบัน หลังจากการ Clarify ใน Draft v2
- หากมีคำถามใหม่เกี่ยวกับ timeout, Manual Verification หรือเจ้าหน้าที่ที่มีสิทธิ์อนุญาตให้ override จะยังไม่สร้างส่วนที่เกี่ยวข้องกับปริศนำนั้นจนกว่าจะได้รับคำตอบที่ชัดเจน
- ข้อที่ยังไม่ได้ตัดสินใจเชิงนโยบายในระดับองค์กร เช่น ระดับสิทธิ์ของเจ้าหน้าที่หรือการกำหนดคนที่สามารถทำ Manual Verification จะถูกชะลอไว้จนกว่าจะได้รับคำตอบอย่างเป็นทางการจากฝ่ายที่เกี่ยวข้อง

