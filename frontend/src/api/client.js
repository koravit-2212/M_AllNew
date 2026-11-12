// จุดเดียวที่หน้าจอใช้เรียก API หลังบ้าน (ตามสัญญา API ใน plan.md ข้อ 4)
// ตอน test ให้ส่ง client จำลองเข้าไปในหน้าจอแทน ไม่ต้องรันหลังบ้านจริง
// เรียกผ่าน /api (ดู proxy ใน vite.config.js) หลังบ้านต้องรันอยู่ที่ port 8000
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

// FR-EQP-05, Q-10: อ่าน HTTP status จาก error ที่ client โยน (มี .status หรือข้อความ "... failed: <status>")
export function getErrorStatus(error) {
  if (typeof error?.status === 'number') return error.status
  const match = String(error?.message ?? '').match(/failed: (\d{3})/)
  return match ? Number(match[1]) : null
}

export const api = {
  async searchBooks({ q, page = 1, per_page = 20 }) {
    const params = new URLSearchParams({ q, page: String(page), per_page: String(per_page) })
    const res = await fetch(`${BASE}/search?${params}`)
    if (!res.ok) {
      throw new Error(`Search request failed: ${res.status}`)
    }
    return res.json()
  },
  async getBookDetail(titleId) {
    const res = await fetch(`${BASE}/books/${encodeURIComponent(titleId)}`)
    if (!res.ok) {
      throw new Error(`Book detail request failed: ${res.status}`)
    }
    return res.json()
  },
  // FR-EQP-01, FR-EQP-02: ประเภทอุปกรณ์ที่ยืมได้พร้อมจำนวนคงเหลือ (GET /api/equipment-types)
  async listEquipmentTypes() {
    const res = await fetch(`${BASE}/equipment-types`)
    if (!res.ok) {
      throw new Error(`Equipment types request failed: ${res.status}`)
    }
    return res.json()
  },
  // FR-EQP-03: นักศึกษาตัวอย่างให้เลือก (ชั่วคราวจนกว่าจะมีล็อกอิน 001/002)
  async listStudents() {
    const res = await fetch(`${BASE}/students`)
    if (!res.ok) {
      throw new Error(`Students request failed: ${res.status}`)
    }
    return res.json()
  },
  // FR-EQP-02, ASM-01: ส่งคำขอยืม ได้คำขอสถานะรออนุมัติ (POST /api/loan-requests)
  async createLoanRequest({ studentId, equipmentTypeId, quantity }) {
    const res = await fetch(`${BASE}/loan-requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, equipment_type_id: equipmentTypeId, quantity }),
    })
    if (!res.ok) {
      const error = new Error(`Loan request failed: ${res.status}`)
      error.status = res.status
      throw error
    }
    return res.json()
  },
  // FR-EQP-03: คำขอยืมที่รอเจ้าหน้าที่ตรวจสอบ พร้อมข้อมูลนักศึกษาและรายการค้างคืน
  async listPendingLoanRequests() {
    const res = await fetch(`${BASE}/loan-requests`)
    if (!res.ok) {
      throw new Error(`Pending loan requests failed: ${res.status}`)
    }
    return res.json()
  },
  // FR-EQP-04: เจ้าหน้าที่อนุมัติ ได้จำนวนคงเหลือใหม่กลับมา
  async approveLoanRequest(requestId) {
    const res = await fetch(`${BASE}/loan-requests/${encodeURIComponent(requestId)}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    if (!res.ok) {
      throw new Error(`Approve failed: ${res.status}`)
    }
    return res.json()
  },
  // FR-EQP-06, ASM-02, Q-04: เจ้าหน้าที่ปลดล็อก (override) เป็นกรณีพิเศษ เมื่อนักศึกษามีรายการค้างคืน
  async overrideLoanRequest(requestId) {
    const res = await fetch(`${BASE}/loan-requests/${encodeURIComponent(requestId)}/override`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    if (!res.ok) {
      throw new Error(`Override failed: ${res.status}`)
    }
    return res.json()
  },
  async getSlots({ dateFrom, packageCode }) {
    const q = new URLSearchParams({ date_from: dateFrom, package_code: packageCode })
    const res = await fetch(`${BASE}/slots?${q}`)
    return res.json()
  },
  async createBooking({ slotId }) {
    const res = await fetch(`${BASE}/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slot_id: slotId }),
    })
    return { status: res.status, body: await res.json() }
  },
}
