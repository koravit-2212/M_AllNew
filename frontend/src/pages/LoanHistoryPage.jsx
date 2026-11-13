import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-LNS-07, AC-LNS-04
// หน้าประวัติการยืม-คืนแสดงรายการจริงจาก member history พร้อมสถานะคืนแล้ว/ยังไม่คืน/ค่าปรับ

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('th-TH', { day: 'numeric', month: 'short', year: 'numeric' }).format(date)
}

function getDisplayStatus(record) {
  if (record?.status === 'returned') {
    return 'คืนแล้ว'
  }
  if (record?.status === 'borrowed') {
    return 'ยังไม่คืน'
  }
  if (Number(record?.penalty_amount ?? 0) > 0) {
    return `ค่าปรับ ${Number(record.penalty_amount)} บาท`
  }
  return record?.status || 'ไม่ระบุ'
}

function getStatusTone(record) {
  if (record?.status === 'returned') {
    return 'green'
  }
  if (record?.status === 'borrowed') {
    return 'red'
  }
  if (Number(record?.penalty_amount ?? 0) > 0) {
    return 'amber'
  }
  return 'neutral'
}

function getPenaltyText(record) {
  const penalty = Number(record?.penalty_amount ?? 0)
  return penalty > 0 ? `ค่าปรับ ${penalty} บาท` : null
}

export default function LoanHistoryPage({ client = api, defaultMemberId = 'STD-1001' }) {
  const [memberId, setMemberId] = useState(defaultMemberId)
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [hasLoaded, setHasLoaded] = useState(false)

  const loadHistory = async (nextMemberId = memberId) => {
    const normalizedMemberId = String(nextMemberId || '').trim()
    if (!normalizedMemberId) {
      setErrorMessage('กรุณากรอกรหัสสมาชิก')
      setRecords([])
      return
    }

    setLoading(true)
    setErrorMessage('')
    try {
      const payload = await client.getLoanHistory({ memberId: normalizedMemberId })
      setRecords(payload?.history ?? [])
      setHasLoaded(true)
    } catch (error) {
      const detail = typeof error?.detail === 'string' ? error.detail : error?.message || 'ไม่สามารถโหลดประวัติได้'
      setRecords([])
      setErrorMessage(detail)
      setHasLoaded(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadHistory(defaultMemberId)
  }, [defaultMemberId])

  const handleSubmit = (event) => {
    event.preventDefault()
    void loadHistory(memberId)
  }

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">Loan History</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-800">ประวัติการยืม-คืน</h1>
          </div>
        </div>

        <form className="mt-6 flex flex-col gap-3 md:flex-row" onSubmit={handleSubmit}>
          <label className="flex-1 text-sm font-medium text-slate-700" htmlFor="member-id-history">
            <span className="mb-2 block">รหัสสมาชิก</span>
            <input
              id="member-id-history"
              type="text"
              value={memberId}
              onChange={(event) => setMemberId(event.target.value)}
              placeholder="เช่น STD-1001"
              className="w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-base text-slate-800 outline-none focus:border-teal-700 focus:bg-white"
            />
          </label>
          <button
            type="submit"
            disabled={loading || !memberId.trim()}
            className="self-end rounded-xl bg-teal-700 px-5 py-3 text-base font-bold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? 'กำลังโหลด...' : 'ดูประวัติ'}
          </button>
        </form>

        {errorMessage ? (
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{errorMessage}</div>
        ) : null}

        {hasLoaded && records.length === 0 && !loading ? (
          <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            ยังไม่มีประวัติการยืม-คืนสำหรับสมาชิกนี้
          </div>
        ) : null}

        {records.length > 0 ? (
          <div className="mt-6 space-y-3">
            {records.map((record) => {
              const statusLabel = getDisplayStatus(record)
              const penaltyText = getPenaltyText(record)
              const tone = getStatusTone(record)
              const badgeClass = {
                green: 'bg-emerald-100 text-emerald-800',
                amber: 'bg-amber-100 text-amber-900',
                red: 'bg-rose-100 text-rose-800',
                neutral: 'bg-slate-100 text-slate-700',
              }[tone]

              return (
                <article key={record.loan_id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                      <div className="text-lg font-bold text-slate-800">{record.title || record.copy_id || 'หนังสือ'}</div>
                      <div className="mt-1 text-sm text-slate-600">
                        ยืม {formatDate(record.borrow_date)}
                        {record.return_date ? ` · คืน ${formatDate(record.return_date)}` : ''}
                      </div>
                    </div>
                    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${badgeClass}`}>{statusLabel}</span>
                  </div>

                  {penaltyText ? <div className="mt-2 text-sm font-medium text-amber-800">{penaltyText}</div> : null}

                  <div className="mt-3 grid gap-2 text-sm text-slate-700 sm:grid-cols-2">
                    <div className="rounded-xl bg-white px-3 py-2">
                      <span className="text-slate-500">วันครบกำหนด:</span> {formatDate(record.due_date)}
                    </div>
                    <div className="rounded-xl bg-white px-3 py-2">
                      <span className="text-slate-500">สถานะ:</span>{' '}
                      {record?.status === 'returned' ? 'returned' : record?.status === 'borrowed' ? 'borrowed' : record?.status || 'ไม่ระบุ'}
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        ) : null}
      </section>
    </main>
  )
}
