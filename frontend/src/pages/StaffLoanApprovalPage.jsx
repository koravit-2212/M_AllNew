import { useCallback, useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-EQP-03, FR-EQP-04, FR-EQP-06, NFR-USB-01
// หน้าเจ้าหน้าที่ตรวจสอบและอนุมัติคำขอยืมอุปกรณ์ (UI-EQP-02)
// FR-EQP-04 (Q-03): แสดงกำหนดคืนก่อนและหลังอนุมัติ
// FR-EQP-06, ASM-02 (Q-04): นักศึกษามีรายการค้างคืน ปุ่มอนุมัติปกติถูกบล็อก เหลือปุ่ม override

function Row({ label, children }) {
  return (
    <div className="flex justify-between gap-3 py-1">
      <span className="whitespace-nowrap text-slate-500">{label}</span>
      <span className="text-right">{children}</span>
    </div>
  )
}

// FR-EQP-04: แสดง due date (YYYY-MM-DD จากหลังบ้าน) เป็นวันที่แบบไทย เช่น "ศ. 13 พ.ย. 2569"
function formatDueDate(isoDate) {
  if (!isoDate) return ''
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day).toLocaleDateString('th-TH', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

// FR-EQP-06: ข้อความรายการค้างคืนแต่ละรายการ ตาม UI-EQP-02 เช่น "ร่ม — เกินกำหนด 2 วัน"
function formatOutstanding(item) {
  return `${item.item} — เกินกำหนด ${item.days_overdue} วัน`
}

export default function StaffLoanApprovalPage({ client = api }) {
  const [requests, setRequests] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [result, setResult] = useState(null)
  const [approving, setApproving] = useState(false)

  // FR-EQP-03: โหลดคำขอที่รอเจ้าหน้าที่ตรวจสอบ
  const loadRequests = useCallback(async () => {
    try {
      const payload = await client.listPendingLoanRequests()
      setRequests(payload?.items ?? [])
    } catch {
      setRequests([])
    }
  }, [client])

  useEffect(() => {
    loadRequests()
  }, [loadRequests])

  const selected = requests.find((request) => request.request_id === selectedId)

  // FR-EQP-04: อนุมัติ (หรือ override ตาม ASM-02) แล้วแสดงว่าบันทึกการยืมแล้ว พร้อมจำนวนคงเหลือใหม่
  const approve = async (override = false) => {
    if (!selected) return
    setApproving(true)
    try {
      const loan = override
        ? await client.overrideLoanRequest(selected.request_id)
        : await client.approveLoanRequest(selected.request_id)
      setResult({ name: loan.equipment_name, availableCount: loan.available_count, dueDate: loan.due_date })
      setSelectedId(null)
      await loadRequests()
    } catch {
      setResult(null)
    } finally {
      setApproving(false)
    }
  }

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-800">อนุมัติคำขอยืมอุปกรณ์ (เจ้าหน้าที่)</h1>

        {result && (
          <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center text-emerald-900" role="status">
            <b className="block text-xl">บันทึกการยืมแล้ว</b>
            <small className="mt-1 block text-sm">
              {result.name}คงเหลือ {result.availableCount}
            </small>
          </div>
        )}
        {result?.dueDate && (
          <div className="mt-3 rounded-xl border border-slate-200 px-4 py-3 text-sm" aria-label="กำหนดคืนที่บันทึก">
            <Row label="กำหนดคืน">{formatDueDate(result.dueDate)}</Row>
          </div>
        )}

        <ul className="mt-4 space-y-2" aria-label="คำขอที่รอตรวจสอบ">
          {requests.map((request) => {
            const isSelected = request.request_id === selectedId
            return (
              <li key={request.request_id}>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedId(request.request_id)
                    setResult(null)
                  }}
                  aria-pressed={isSelected}
                  className={`w-full rounded-xl px-4 py-3 text-left text-sm transition ${
                    isSelected ? 'border-2 border-teal-700 bg-teal-50' : 'border border-slate-200 bg-white hover:bg-slate-50'
                  }`}
                >
                  {request.student.name} ({request.student.student_id}) · {request.equipment.name} × {request.quantity}
                </button>
              </li>
            )
          })}
        </ul>

        {selected && (
          <div className="mt-4">
            <div className="rounded-xl border border-slate-200 px-4 py-3 text-sm" aria-label="ข้อมูลคำขอ">
              <Row label="นักศึกษา">
                {selected.student.name} ({selected.student.student_id})
              </Row>
              <Row label="อุปกรณ์">
                {selected.equipment.name} × {selected.quantity}
              </Row>
              {selected.outstanding_items.length === 0 && <Row label="รายการค้างคืน">ไม่มี</Row>}
            </div>
            {selected.due_date && (
              <div className="mt-3 rounded-xl border border-slate-200 px-4 py-3 text-sm">
                <Row label="กำหนดคืน (due date)">{formatDueDate(selected.due_date)}</Row>
              </div>
            )}
            {selected.outstanding_items.length > 0 && (
              <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900" role="alert">
                <b className="block text-base">มีรายการค้างคืน</b>
                <ul>
                  {selected.outstanding_items.map((item, index) => (
                    <li key={`${item.item}-${index}`}>{formatOutstanding(item)}</li>
                  ))}
                </ul>
                <p>ระบบบล็อกการยืมใหม่จนกว่าจะคืนและชำระค่าปรับ</p>
              </div>
            )}
            {selected.outstanding_items.length > 0 ? (
              <button
                type="button"
                onClick={() => approve(true)}
                disabled={approving}
                className="mt-4 w-full rounded-xl border border-teal-700 bg-white px-4 py-3 font-bold text-teal-700 disabled:opacity-50"
              >
                ปลดล็อก (override) เป็นกรณีพิเศษ
              </button>
            ) : (
              <button
                type="button"
                onClick={() => approve(false)}
                disabled={approving}
                className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white disabled:bg-slate-300"
              >
                อนุมัติการยืม
              </button>
            )}
          </div>
        )}
      </section>
    </main>
  )
}
