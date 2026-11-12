import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-BKG-01, FR-BKG-03, NFR-USB-01
// หน้าจองพื้นที่ในห้องสมุด (UI-BKG-01) ขั้น 1 เลือกพื้นที่และช่วงเวลา ขั้น 2 ยืนยัน ขั้น 3 ผลการจอง
// FR-BKG-04: พื้นที่ไม่ว่าง (409) แจ้งให้เลือกพื้นที่หรือเวลาอื่น และกลับไปเลือกใหม่ได้

const STEPS = ['1 เลือกพื้นที่', '2 ยืนยัน', '3 ผลการจอง']

// UI-BKG-01: แสดงเวลา "09:00" เป็น "09.00" และช่วงเวลาเป็น "09.00–11.00 น."
export function formatSlotTime(slot) {
  const dot = (value) => String(value).replace(':', '.')
  return `${dot(slot.start_time)}–${dot(slot.end_time)} น.`
}

function Steps({ current }) {
  return (
    <ol className="mt-3 flex gap-2" aria-label="ขั้นตอนการจอง">
      {STEPS.map((label, index) => (
        <li
          key={label}
          aria-current={index === current ? 'step' : undefined}
          className={`flex-1 rounded-full px-2 py-1 text-center text-xs ${
            index === current ? 'bg-teal-700 text-white' : 'bg-slate-100 text-slate-500'
          }`}
        >
          {label}
        </li>
      ))}
    </ol>
  )
}

// FR-BKG-03: วันที่แบบไทย เช่น "ศ. 13 พ.ย. 2569"
function formatThaiDate(isoDate) {
  if (!isoDate) return ''
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day).toLocaleDateString('th-TH', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function SummaryCard({ space, slot, withDate = true }) {
  return (
    <div className="mt-3 rounded-xl border border-slate-200 px-4 py-3 text-sm" aria-label="รายละเอียดการจอง">
      <div className="flex justify-between gap-3 py-1">
        <span className="text-slate-500">พื้นที่</span>
        <span className="text-right">{space.facility_name}</span>
      </div>
      {withDate && (
        <div className="flex justify-between gap-3 py-1">
          <span className="text-slate-500">วันที่</span>
          <span className="text-right">{formatThaiDate(slot.date)}</span>
        </div>
      )}
      <div className="flex justify-between gap-3 py-1">
        <span className="text-slate-500">เวลา</span>
        <span className="text-right">{formatSlotTime(slot)}</span>
      </div>
    </div>
  )
}

function StatusBadge({ available }) {
  return available ? (
    <span className="rounded-full bg-emerald-100 px-3 py-0.5 text-xs text-emerald-700">ว่าง</span>
  ) : (
    <span className="rounded-full bg-rose-100 px-3 py-0.5 text-xs text-rose-700">เต็ม</span>
  )
}

export default function SpaceBookingPage({ client = api }) {
  const [spaces, setSpaces] = useState([])
  const [spaceId, setSpaceId] = useState(null)
  const [slotId, setSlotId] = useState(null)
  const [users, setUsers] = useState([])
  const [userId, setUserId] = useState('')
  // step: 'select' | 'confirm' | 'done'
  const [step, setStep] = useState('select')
  const [booked, setBooked] = useState(null)
  // null | 'unavailable' (409, FR-BKG-04) | 'not_eligible' (403, CON-ELG-01) | 'failed' (Q-04)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  // FR-BKG-01: โหลดพื้นที่ที่ใช้งานได้พร้อมช่วงเวลา และผู้ใช้ตัวอย่าง (Q-01)
  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const payload = await client.listAvailableSpaces()
        if (active) setSpaces(payload?.spaces ?? [])
      } catch {
        if (active) setSpaces([])
      }
      try {
        const payload = await client.listSpaceUsers?.()
        if (active) {
          const list = payload?.items ?? []
          setUsers(list)
          setUserId((current) => current || list[0]?.userId || '')
        }
      } catch {
        if (active) setUsers([])
      }
    }
    load()
    return () => {
      active = false
    }
  }, [client, reloadKey])

  const selectedSpace = spaces.find((space) => space.space_id === spaceId)
  const selectedSlot = selectedSpace?.slots.find((slot) => slot.slot_id === slotId)

  // กลับไปขั้นเลือก และโหลดสถานะว่างใหม่
  const backToSelect = () => {
    setStep('select')
    setSlotId(null)
    setError(null)
    setBooked(null)
    setReloadKey((key) => key + 1)
  }

  // FR-BKG-02, FR-BKG-03: ยืนยันการจอง หลังบ้านตรวจความว่างและบันทึกแบบ atomic
  const confirm = async () => {
    if (!selectedSpace || !selectedSlot || !userId) return
    setSubmitting(true)
    setError(null)
    try {
      await client.createReservation({
        userId,
        spaceId: selectedSpace.space_id,
        date: selectedSlot.date,
        startTime: selectedSlot.start_time,
        endTime: selectedSlot.end_time,
      })
      setBooked({ space: selectedSpace, slot: selectedSlot })
      setStep('done')
    } catch (err) {
      if (err?.status === 409) setError('unavailable')
      else setError(err?.status === 403 ? 'not_eligible' : 'failed')
    } finally {
      setSubmitting(false)
    }
  }

  if (step === 'done' && booked) {
    return (
      <main className="mx-auto max-w-4xl p-4 md:p-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
          <h1 className="text-2xl font-bold text-slate-800">จองพื้นที่ในห้องสมุด</h1>
          <Steps current={2} />
          <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center text-emerald-900" role="status">
            <b className="block text-xl">จองสำเร็จ</b>
            <small className="mt-1 block text-sm">บันทึกการจองแล้ว</small>
          </div>
          <SummaryCard space={booked.space} slot={booked.slot} />
          <button
            type="button"
            onClick={backToSelect}
            className="mt-4 w-full rounded-xl border border-teal-700 bg-white px-4 py-3 font-bold text-teal-700"
          >
            กลับหน้าหลัก
          </button>
        </section>
      </main>
    )
  }

  if (step === 'confirm' && selectedSpace && selectedSlot && error === 'unavailable') {
    return (
      <main className="mx-auto max-w-4xl p-4 md:p-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
          <h1 className="text-2xl font-bold text-slate-800">จองพื้นที่ในห้องสมุด</h1>
          <Steps current={1} />
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800" role="alert">
            <b className="block text-base">พื้นที่ไม่ว่างในช่วงเวลานี้</b>
            กรุณาเลือกพื้นที่หรือเวลาอื่น ระบบไม่ได้สร้างรายการจองซ้อน
          </div>
          <SummaryCard space={selectedSpace} slot={selectedSlot} withDate={false} />
          <button
            type="button"
            onClick={backToSelect}
            className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white"
          >
            กลับไปเลือกพื้นที่/เวลาใหม่
          </button>
        </section>
      </main>
    )
  }

  if (step === 'confirm' && selectedSpace && selectedSlot) {
    return (
      <main className="mx-auto max-w-4xl p-4 md:p-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
          <h1 className="text-2xl font-bold text-slate-800">จองพื้นที่ในห้องสมุด</h1>
          <Steps current={1} />
          {error && (
            <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800" role="alert">
              <b className="block text-base">{error === 'not_eligible' ? 'ไม่มีสิทธิ์จองพื้นที่' : 'จองไม่สำเร็จ กรุณาลองใหม่'}</b>
            </div>
          )}
          <SummaryCard space={selectedSpace} slot={selectedSlot} />
          <button
            type="button"
            onClick={confirm}
            disabled={submitting}
            className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white disabled:bg-slate-300"
          >
            ยืนยันการจอง
          </button>
          <button
            type="button"
            onClick={() => {
              setStep('select')
              setError(null)
            }}
            className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-700"
          >
            กลับ
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-800">จองพื้นที่ในห้องสมุด</h1>
        <Steps current={0} />

        {/* ชั่วคราว: เลือกผู้ใช้ตัวอย่างเป็นผู้จอง จนกว่าจะมีระบบยืนยันตัวตน (Q-01) */}
        <label htmlFor="space-user" className="mt-4 block text-sm text-slate-500">
          ผู้จอง
        </label>
        <select
          id="space-user"
          value={userId}
          onChange={(event) => setUserId(event.target.value)}
          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2"
        >
          {users.map((user) => (
            <option key={user.userId} value={user.userId}>
              {user.name} ({user.userId})
            </option>
          ))}
        </select>

        <p id="space-list-label" className="mt-4 text-sm text-slate-500">
          พื้นที่ที่ใช้งานได้
        </p>
        <ul className="mt-2 space-y-2" aria-labelledby="space-list-label">
          {spaces.map((space) => {
            const selected = space.space_id === spaceId
            return (
              <li key={space.space_id}>
                <button
                  type="button"
                  disabled={!space.available}
                  aria-pressed={selected}
                  onClick={() => {
                    setSpaceId(space.space_id)
                    setSlotId(null)
                  }}
                  className={`flex w-full items-center justify-between gap-3 rounded-xl px-4 py-3 text-left transition disabled:bg-slate-50 disabled:opacity-60 ${
                    selected ? 'border-2 border-teal-700 bg-teal-50' : 'border border-slate-200 bg-white hover:bg-slate-50'
                  }`}
                >
                  <span>
                    <span className="block font-bold text-slate-800">{space.facility_name}</span>
                    <span className="block text-sm text-slate-500">{space.available ? 'ว่างวันนี้' : 'ไม่ว่างวันนี้'}</span>
                  </span>
                  <StatusBadge available={space.available} />
                </button>
              </li>
            )
          })}
        </ul>

        {selectedSpace && (
          <>
            <p id="slot-list-label" className="mt-4 text-sm text-slate-500">
              ช่วงเวลา
            </p>
            <ul className="mt-2 space-y-2" aria-labelledby="slot-list-label">
              {selectedSpace.slots.map((slot) => {
                const selected = slot.slot_id === slotId
                return (
                  <li key={slot.slot_id}>
                    <button
                      type="button"
                      disabled={!slot.available}
                      aria-pressed={selected}
                      onClick={() => setSlotId(slot.slot_id)}
                      className={`flex w-full items-center justify-between rounded-xl px-4 py-3 text-left text-sm transition disabled:bg-slate-50 disabled:opacity-60 ${
                        selected ? 'border-2 border-teal-700 bg-teal-50' : 'border border-slate-200 bg-white hover:bg-slate-50'
                      }`}
                    >
                      <span>{formatSlotTime(slot)}</span>
                      <small className="text-slate-500">{slot.available ? 'ว่าง' : 'เต็ม'}</small>
                    </button>
                  </li>
                )
              })}
            </ul>
          </>
        )}

        <button
          type="button"
          onClick={() => setStep('confirm')}
          disabled={!selectedSlot || !userId}
          className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white disabled:bg-slate-300"
        >
          ถัดไป
        </button>
      </section>
    </main>
  )
}
