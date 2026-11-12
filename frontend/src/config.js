// ตัวเลขและกฎจาก spec ที่หน้าจอใช้ อยู่ที่เดียว (ตาราง "ค่าที่ตั้งได้" ใน specs/007-equipment/plan.md)

// FR-EQP-02, Q-11: นักศึกษาขอยืมอุปกรณ์ได้ครั้งละ 1 ชิ้นต่อคำขอ
export const EQUIPMENT_REQUEST_QUANTITY = 1

// FR-ACC-01, FR-ACC-03: วิธีการสแกนที่ยอมรับและผลลัพธ์การเข้าใช้บริการในหน้าจอ kiosk
export const ACCESS_SCAN_METHODS = [
  { key: 'qr', label: 'QR Code' },
  { key: 'card', label: 'บัตรนักศึกษา' },
]

export const ACCESS_DEFAULT_OCCUPANCY = 128
