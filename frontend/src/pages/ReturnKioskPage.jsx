import { useState } from 'react'

import { api } from '../api/client.js'

// FR-LNS-05, FR-LNS-06, AC-LNS-03
// หน้าเครื่องคืนหนังสือแสดงผลสำเร็จ พร้อมจำนวนวันที่เกินกำหนดและค่าปรับทันทีหลังบันทึกคืน

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

export default function ReturnKioskPage({ client = api }) {
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
      const payload = await client.returnBook({ memberId: normalizedMemberId, barcode: normalizedBarcode })
      setResult(payload)
    } catch (error) {
      const detail = typeof error?.detail === 'string' ? error.detail : error?.message || 'ไม่สามารถคืนหนังสือได้'
      setResult({ status: 'error', message: detail })
      setErrorMessage(detail)
    } finally {
      setLoading(false)
    }
  }

  const overdueDays = Number(result?.overdue_days ?? 0)
  const penaltyAmount = Number(result?.penalty_amount ?? 0)
  const isSuccess = result?.status === 'returned' || result?.status === 'approved'
  const overdue = overdueDays > 0

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">Return Kiosk</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-800">คืนหนังสือ</h1>
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
            {loading ? 'กำลังคืน...' : 'คืนหนังสือ'}
          </button>
        </form>

        {errorMessage ? (
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {errorMessage}
          </div>
        ) : null}

        {isSuccess && result ? (
          <div className="mt-6 space-y-4">
            <StatusCard
              tone="success"
              title="คืนสำเร็จ"
              message={result.message || 'บันทึกการคืนแล้ว'}
              detail={overdue ? undefined : 'บันทึกการคืนแล้ว'}
            />

            {overdue ? (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                <div className="font-semibold">เกินกำหนด {overdueDays} วัน</div>
                <div className="mt-1">ค่าปรับ {penaltyAmount} บาท</div>
              </div>
            ) : (
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                บันทึกการคืนแล้วโดยไม่มีค่าปรับเพิ่มเติม
              </div>
            )}
          </div>
        ) : null}
      </section>
    </main>
  )
}
