import { useState } from 'react'

import { api } from '../api/client.js'

// FR-LNS-01, FR-LNS-02, FR-LNS-03, FR-LNS-04, CON-LNS-01
// หน้าจอเครื่องยืมหนังสือสำหรับบันทึกการยืมและแสดงผลสำเร็จ/ปฏิเสธตามกติกา AC-LNS-01 และ AC-LNS-02

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('th-TH', { day: 'numeric', month: 'short', year: 'numeric' }).format(date)
}

function StatusCard({ tone = 'neutral', title, message, detail }) {
  const toneClass = {
    success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
    danger: 'border-rose-200 bg-rose-50 text-rose-900',
    warning: 'border-amber-200 bg-amber-50 text-amber-900',
    neutral: 'border-slate-200 bg-slate-50 text-slate-800',
  }[tone]

  return (
    <div className={`rounded-2xl border p-5 ${toneClass}`} role="alert">
      <div className="text-xl font-bold">{title}</div>
      <div className="mt-2 text-sm font-medium">{message}</div>
      {detail ? <div className="mt-2 text-sm opacity-80">{detail}</div> : null}
    </div>
  )
}

export default function LoanKioskPage({ client = api }) {
  const [memberId, setMemberId] = useState('')
  const [barcode, setBarcode] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    const normalizedMemberId = memberId.trim()
    const normalizedBarcode = barcode.trim()
    if (!normalizedMemberId || !normalizedBarcode) {
      setErrorMessage('กรุณากรอกรหัสสมาชิกและบาร์โค้ดหนังสือ')
      return
    }

    setLoading(true)
    setErrorMessage('')
    try {
      const payload = await client.borrowBook({ memberId: normalizedMemberId, barcode: normalizedBarcode, source: 'counter' })
      setResult(payload)
    } catch (error) {
      const detail = typeof error?.detail === 'string' ? error.detail : error?.message || 'ไม่สามารถยืมได้'
      const message = detail.includes('ครบจำนวนหนังสือ') ? 'ยืมครบจำนวนหนังสือที่สามารถยืมได้แล้ว' : detail.includes('ถูกยืมอยู่แล้ว') ? 'หนังสือเล่มนี้ถูกยืมอยู่แล้ว' : detail
      setResult({ status: 'denied', message })
      setErrorMessage('')
    } finally {
      setLoading(false)
    }
  }

  const isSuccess = result?.status === 'approved' || result?.allowed === true
  const isDenied = result?.status === 'denied' || result?.status === 'copy_unavailable' || result?.status === 'borrow_limit_exceeded'

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">Borrow Kiosk</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-800">ยืมหนังสือ</h1>
          </div>
        </div>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="member-id" className="mb-2 block text-sm font-medium text-slate-700">
              รหัสสมาชิก
            </label>
            <input
              id="member-id"
              type="text"
              value={memberId}
              onChange={(event) => setMemberId(event.target.value)}
              placeholder="เช่น STD-1001"
              className="w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-base text-slate-800 outline-none focus:border-teal-700 focus:bg-white"
            />
          </div>

          <div>
            <label htmlFor="book-barcode" className="mb-2 block text-sm font-medium text-slate-700">
              บาร์โค้ด / QR Code หนังสือ
            </label>
            <input
              id="book-barcode"
              type="text"
              value={barcode}
              onChange={(event) => setBarcode(event.target.value)}
              placeholder="เช่น BC-001"
              className="w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-base text-slate-800 outline-none focus:border-teal-700 focus:bg-white"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !memberId.trim() || !barcode.trim()}
            className="w-full rounded-xl bg-teal-700 px-4 py-3 text-base font-bold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? 'กำลังยืม...' : 'ยืมหนังสือ'}
          </button>
        </form>

        {errorMessage ? (
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {errorMessage}
          </div>
        ) : null}

        {isSuccess && result ? (
          <div className="mt-6">
            <StatusCard
              tone="success"
              title="ยืมสำเร็จ"
              message={result.message || 'บันทึกรายการยืมแล้ว'}
              detail={`กำหนดคืน: ${formatDate(result.due_date)}`}
            />
            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
              <div className="flex justify-between gap-3 py-1">
                <span className="text-slate-500">หนังสือ</span>
                <span>{result.copy_name || 'หนังสือเลือกใช้'}</span>
              </div>
              <div className="flex justify-between gap-3 py-1">
                <span className="text-slate-500">วันที่ยืม</span>
                <span>{formatDate(result.borrow_date || new Date().toISOString().slice(0, 10))}</span>
              </div>
              <div className="flex justify-between gap-3 py-1">
                <span className="text-slate-500">กำหนดคืน</span>
                <span>{formatDate(result.due_date)}</span>
              </div>
            </div>
            <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
              ระบบจะแจ้งเตือนล่วงหน้า 1–3 วันก่อนกำหนดคืน ผ่านระบบแจ้งเตือนและอีเมล
            </div>
          </div>
        ) : null}

        {isDenied && result ? (
          <div className="mt-6">
            <StatusCard
              tone="danger"
              title="ไม่สามารถยืมได้"
              message={result.message || 'ยืมหนังสือไม่สำเร็จ'}
              detail="กรุณาตรวจสอบข้อมูลหรือปรับเงื่อนไขก่อนทำรายการอีกครั้ง"
            />
          </div>
        ) : null}
      </section>
    </main>
  )
}
