import { useEffect, useState } from 'react'

import { api } from '../api/client.js'
import { ACCESS_DEFAULT_OCCUPANCY, ACCESS_SCAN_METHODS } from '../config.js'

// FR-ACC-01, FR-ACC-04, FR-ACC-05, CON-SEC-01
// หน้าจอ kiosk สำหรับสแกนบัตร/QR และแสดงสถานะยืนยันตัวตนแบบ Real-time
// พื้นฐานของ AC-ACC-01 / AC-ACC-02 / AC-ACC-03 ที่ทำต่อจาก T-03

function formatTime(value) {
  if (!value) return '—'
  if (typeof value === 'string') return value
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
}

function StatusCard({ tone = 'neutral', title, message, detail }) {
  const toneClass = {
    success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
    warning: 'border-amber-200 bg-amber-50 text-amber-900',
    danger: 'border-rose-200 bg-rose-50 text-rose-900',
    neutral: 'border-slate-200 bg-slate-50 text-slate-800',
  }[tone]

  return (
    <div className={`rounded-2xl border p-5 ${toneClass}`} role={tone === 'neutral' ? 'status' : 'alert'}>
      <div className="text-xl font-bold">{title}</div>
      <div className="mt-2 text-sm font-medium">{message}</div>
      {detail ? <div className="mt-2 text-sm opacity-80">{detail}</div> : null}
    </div>
  )
}

function resolveAccessErrorStatus(error) {
  const detail = typeof error?.detail === 'string' ? error.detail : error?.message || ''
  if (detail.includes('ไม่พบข้อมูล')) return 'not_found'
  if (detail.includes('ไม่มีสิทธิ์')) return 'no_eligibility'
  if (detail.includes('ไม่สามารถตรวจสอบสิทธิ์ได้')) return 'verification_failed'
  if (error?.status === 404) return 'not_found'
  if (error?.status === 403) return 'no_eligibility'
  return 'unreadable'
}

export default function AccessKioskPage({ client = api }) {
  const [scanMethod, setScanMethod] = useState(ACCESS_SCAN_METHODS[0].key)
  const [memberInput, setMemberInput] = useState('')
  const [occupancy, setOccupancy] = useState(ACCESS_DEFAULT_OCCUPANCY)
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState('ready')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let active = true
    client
      .getAccessStatus()
      .then((payload) => {
        if (!active) return
        const nextOccupancy = Number(payload?.currentOccupancy ?? payload?.current_occupancy ?? ACCESS_DEFAULT_OCCUPANCY)
        if (Number.isFinite(nextOccupancy)) {
          setOccupancy(nextOccupancy)
        }
      })
      .catch(() => undefined)

    return () => {
      active = false
    }
  }, [client])

  const handleSubmit = async (event) => {
    event.preventDefault()
    const trimmed = memberInput.trim()
    if (!trimmed) return

    setSubmitting(true)
    setStatus('loading')
    try {
      const payload = await client.scanAccess({ scanMethod, qrCodeOrCardId: trimmed })
      setResult(payload)

      const nextStatus = payload?.allowed ? 'success' : payload?.status || 'denied'
      setStatus(nextStatus)

      if (payload?.currentOccupancy != null || payload?.current_occupancy != null) {
        const current = Number(payload?.currentOccupancy ?? payload?.current_occupancy)
        if (Number.isFinite(current)) setOccupancy(current)
      }
    } catch (error) {
      const denialStatus = resolveAccessErrorStatus(error)
      const denialMessage = {
        not_found: 'ไม่พบข้อมูล',
        no_eligibility: 'ไม่มีสิทธิ์',
        verification_failed: 'ไม่สามารถตรวจสอบสิทธิ์ได้',
      }[denialStatus] ?? 'กรุณาลองใหม่หรือติดต่อเจ้าหน้าที่'

      setResult({
        status: denialStatus,
        allowed: false,
        message: denialStatus === 'unreadable' ? 'กรุณาลองใหม่หรือติดต่อเจ้าหน้าที่' : denialMessage,
        errorCode: error?.status ?? 'scan_failed',
      })
      setStatus(denialStatus)
    } finally {
      setSubmitting(false)
    }
  }

  const showSuccess = status === 'success'
  const showWarning = status === 'unreadable' || status === 'not_found' || status === 'no_eligibility' || status === 'verification_failed'

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">Access Kiosk</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-800">สแกนเข้าห้องสมุด</h1>
          </div>
          <div className="rounded-full bg-slate-100 px-3 py-2 text-sm font-medium text-slate-600" aria-label="จำนวนผู้ใช้บริการในอาคาร">
            ผู้ใช้บริการปัจจุบัน {occupancy} คน
          </div>
        </div>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">เลือกวิธีการสแกน</label>
            <div className="flex flex-wrap gap-2" aria-label="วิธีการสแกน">
              {ACCESS_SCAN_METHODS.map((method) => (
                <button
                  key={method.key}
                  type="button"
                  onClick={() => setScanMethod(method.key)}
                  aria-pressed={scanMethod === method.key}
                  className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                    scanMethod === method.key
                      ? 'border-teal-700 bg-teal-700 text-white'
                      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  {method.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="access-member-id" className="mb-2 block text-sm font-medium text-slate-700">
              รหัสบัตร / QR Code
            </label>
            <input
              id="access-member-id"
              type="text"
              value={memberInput}
              onChange={(event) => {
                setMemberInput(event.target.value)
                if (status === 'unreadable' || status === 'not_found' || status === 'no_eligibility' || status === 'verification_failed') {
                  setStatus('ready')
                  setResult(null)
                }
              }}
              placeholder="กรอกรหัสนักศึกษาหรือ QR Code"
              className="w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-base text-slate-800 outline-none ring-0 transition focus:border-teal-700 focus:bg-white"
            />
          </div>

          <button
            type="submit"
            disabled={submitting || !memberInput.trim()}
            className="w-full rounded-xl bg-teal-700 px-4 py-3 text-base font-bold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {submitting ? 'กำลังยืนยัน...' : 'สแกนและยืนยัน'}
          </button>
        </form>

        {showSuccess && result ? (
          <div className="mt-6">
            <StatusCard
              tone="success"
              title="ยืนยันตัวตนสำเร็จ"
              message={result.message === 'ยืนยันตัวตนสำเร็จ' ? 'เชิญเข้าห้องสมุดได้' : (result.message || 'เชิญเข้าห้องสมุดได้')}
              detail={`${result.memberName || 'นักศึกษา'} • ${result.memberId || '—'} • ${formatTime(result.scannedAt)}`}
            />
            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
              <div className="flex justify-between gap-3 py-1">
                <span className="text-slate-500">ชื่อ</span>
                <span>{result.memberName || '—'}</span>
              </div>
              <div className="flex justify-between gap-3 py-1">
                <span className="text-slate-500">รหัส</span>
                <span>{result.memberId || '—'}</span>
              </div>
              <div className="flex justify-between gap-3 py-1">
                <span className="text-slate-500">เวลาเข้า</span>
                <span>{formatTime(result.scannedAt)}</span>
              </div>
            </div>
          </div>
        ) : null}

        {showWarning ? (
          <div className="mt-6">
            <StatusCard
              tone={status === 'unreadable' ? 'warning' : status === 'verification_failed' ? 'danger' : 'warning'}
              title={
                status === 'unreadable'
                  ? 'ไม่สามารถอ่านข้อมูลได้'
                  : status === 'not_found'
                    ? 'ไม่พบข้อมูล'
                    : status === 'no_eligibility'
                      ? 'ไม่มีสิทธิ์'
                      : 'ไม่สามารถตรวจสอบสิทธิ์ได้'
              }
              message={result?.message || 'กรุณาลองใหม่หรือติดต่อเจ้าหน้าที่'}
              detail={status === 'unreadable' ? 'ระบบจะไม่บันทึกการเข้าใช้บริการ' : 'กรุณาลองใหม่หรือติดต่อเจ้าหน้าที่'}
            />
          </div>
        ) : null}

        {status === 'ready' ? (
          <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-600">
            กรุณาเลือกวิธีสแกนและกรอกรหัสบัตรหรือ QR Code เพื่อเริ่มการยืนยันตัวตน
          </div>
        ) : null}
      </section>
    </main>
  )
}
