import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-EQP-01, FR-EQP-02, NFR-USB-01
// หน้ายืมอุปกรณ์ของนักศึกษา (UI-EQP-01) แสดงประเภทอุปกรณ์พร้อมจำนวนคงเหลือให้เลือก
// ปุ่มส่งคำขอเพิ่มใน T-07 และสถานะอุปกรณ์หมดเพิ่มใน T-10
export default function EquipmentLoanPage({ client = api }) {
  const [items, setItems] = useState([])
  const [selectedId, setSelectedId] = useState(null)

  // FR-EQP-01: โหลดรายการประเภทอุปกรณ์จากหลังบ้านเมื่อเข้าหน้า
  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const payload = await client.listEquipmentTypes()
        if (active) {
          setItems(payload?.items ?? [])
        }
      } catch {
        if (active) {
          setItems([])
        }
      }
    }
    load()
    return () => {
      active = false
    }
  }, [client])

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-800">ยืมอุปกรณ์</h1>
        <p id="equipment-choice-label" className="mt-4 text-sm text-slate-500">
          เลือกอุปกรณ์
        </p>
        <ul className="mt-2 space-y-2" aria-labelledby="equipment-choice-label">
          {items.map((item) => {
            const selected = item.equipment_type_id === selectedId
            return (
              <li key={item.equipment_type_id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(item.equipment_type_id)}
                  aria-pressed={selected}
                  className={`flex w-full items-center justify-between gap-3 rounded-xl px-4 py-3 text-left transition ${
                    selected ? 'border-2 border-teal-700 bg-teal-50' : 'border border-slate-200 bg-white hover:bg-slate-50'
                  }`}
                >
                  <span>
                    <span className="block font-bold text-slate-800">{item.name}</span>
                    <span className="block text-sm text-slate-500">คงเหลือ {item.available_count}</span>
                  </span>
                  {item.available_count > 0 && (
                    <span className="rounded-full bg-emerald-100 px-3 py-0.5 text-xs text-emerald-700">ว่าง</span>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </section>
    </main>
  )
}
