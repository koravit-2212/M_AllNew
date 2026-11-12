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
  // FR-PRT-01, Q-07: ส่งข้อมูลไฟล์ที่เลือก (ชื่อ ชนิด ขนาด) ได้ file_id กลับมา error มี .status
  async uploadPrintFile({ filename, contentType, sizeBytes }) {
    const res = await fetch(`${BASE}/print/upload`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, content_type: contentType, size_bytes: sizeBytes }),
    })
    if (!res.ok) {
      const error = new Error(`Print upload failed: ${res.status}`)
      error.status = res.status
      error.detail = (await res.json().catch(() => ({})))?.detail
      throw error
    }
    return res.json()
  },
  // FR-PRT-02: ตัวเลือกการพิมพ์และค่าใช้บริการ
  async getPrintOptions({ fileId, pages, copies, colorMode }) {
    const params = new URLSearchParams({ file_id: fileId, pages: String(pages), copies: String(copies), color_mode: colorMode })
    const res = await fetch(`${BASE}/print/options?${params}`)
    if (!res.ok) {
      throw new Error(`Print options failed: ${res.status}`)
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
