// จุดเดียวที่หน้าจอใช้เรียก API หลังบ้าน (ตามสัญญา API ใน plan.md ข้อ 4)
// ตอน test ให้ส่ง client จำลองเข้าไปในหน้าจอแทน ไม่ต้องรันหลังบ้านจริง
// เรียกผ่าน /api (ดู proxy ใน vite.config.js) หลังบ้านต้องรันอยู่ที่ port 8000
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

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
  // FR-BKG-01: พื้นที่ที่ใช้งานได้พร้อมช่วงเวลาและสถานะว่าง (GET /api/spaces/available)
  async listAvailableSpaces() {
    const res = await fetch(`${BASE}/spaces/available`)
    if (!res.ok) {
      throw new Error(`Available spaces request failed: ${res.status}`)
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
