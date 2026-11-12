import { useCallback, useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-EQP-03, FR-EQP-04, NFR-USB-01
// หน้าเจ้าหน้าที่ตรวจสอบและอนุมัติคำขอยืมอุปกรณ์ (UI-EQP-02)
// ช่อง "กำหนดคืน (due date)" อยู่ใน T-13 และคำเตือนรายการค้างคืนอยู่ใน T-12

function Row({ label, children }) {
  return (
    <div className="flex justify-between gap-3 py-1">
      <span className="whitespace-nowrap text-slate-500">{label}</span>
      <span className="text-right">{children}</span>
    </div>
  )
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

  // FR-EQP-04: อนุมัติ แล้วแสดงว่าบันทึกการยืมแล้ว พร้อมจำนวนคงเหลือใหม่
  const approve = async () => {
    if (!selected) return
    setApproving(true)
    try {
      const loan = await client.approveLoanRequest(selected.request_id)
      setResult({ name: loan.equipment_name, availableCount: loan.available_count })
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
            <button
              type="button"
              onClick={approve}
              disabled={approving}
              className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white disabled:bg-slate-300"
            >
              อนุมัติการยืม
            </button>
          </div>
        )}
      </section>
    </main>
  )
}
