import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-BKG-01, NFR-USB-01
// หน้าจองพื้นที่ในห้องสมุด (UI-BKG-01) ขั้น 1 เลือกพื้นที่และช่วงเวลา
// ขั้นยืนยันและผลการจองเพิ่มใน T-06 สถานะพื้นที่ไม่ว่างเพิ่มใน T-08

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

  // FR-BKG-01: โหลดพื้นที่ที่ใช้งานได้พร้อมช่วงเวลา
  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const payload = await client.listAvailableSpaces()
        if (active) setSpaces(payload?.spaces ?? [])
      } catch {
        if (active) setSpaces([])
      }
    }
    load()
    return () => {
      active = false
    }
  }, [client])

  const selectedSpace = spaces.find((space) => space.space_id === spaceId)

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-800">จองพื้นที่ในห้องสมุด</h1>
        <Steps current={0} />

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
      </section>
    </main>
  )
}
