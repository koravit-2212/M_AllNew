import { useEffect, useState } from 'react'

import { api, getErrorStatus } from '../api/client.js'
import { EQUIPMENT_REQUEST_QUANTITY } from '../config.js'

// FR-EQP-01, FR-EQP-02, FR-EQP-05, ASM-01, NFR-USB-01
// หน้ายืมอุปกรณ์ของนักศึกษา (UI-EQP-01) แสดงประเภทอุปกรณ์ให้เลือก แล้วส่งคำขอให้เจ้าหน้าที่อนุมัติ
// อุปกรณ์ที่หมดแสดงป้าย "หมด" ข้อความ "ไม่สามารถยืมได้" และกดส่งคำขอไม่ได้

// FR-EQP-02, Q-11: จำนวนต่อคำขอมาจาก config
const REQUEST_QUANTITY = EQUIPMENT_REQUEST_QUANTITY

export default function EquipmentLoanPage({ client = api }) {
  const [items, setItems] = useState([])
  const [students, setStudents] = useState([])
  const [studentId, setStudentId] = useState('')
  const [selectedId, setSelectedId] = useState(null)
  const [submitted, setSubmitted] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  // null | 'out_of_stock' (409, FR-EQP-05) | 'failed' (เหตุอื่น, Q-10)
  const [submitError, setSubmitError] = useState(null)

  // FR-EQP-01: โหลดรายการประเภทอุปกรณ์ และนักศึกษาตัวอย่าง (ชั่วคราวจนกว่าจะมีล็อกอิน) เมื่อเข้าหน้า
  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const payload = await client.listEquipmentTypes()
        if (active) setItems(payload?.items ?? [])
      } catch {
        if (active) setItems([])
      }
      try {
        const payload = await client.listStudents()
        if (active) {
          const list = payload?.items ?? []
          setStudents(list)
          setStudentId((current) => current || list[0]?.student_id || '')
        }
      } catch {
        if (active) setStudents([])
      }
    }
    load()
    return () => {
      active = false
    }
  }, [client])

  const selectedItem = items.find((item) => item.equipment_type_id === selectedId)
  // FR-EQP-02, FR-EQP-05: ตรวจจำนวนคงเหลือก่อนให้ส่งคำขอ
  const selectedOutOfStock = Boolean(selectedItem) && selectedItem.available_count < REQUEST_QUANTITY

  // FR-EQP-02, ASM-01: ส่งคำขอยืม ผลคือรอเจ้าหน้าที่ตรวจสอบและอนุมัติ ไม่ใช่ยืมได้ทันที
  const submitRequest = async () => {
    if (!selectedItem || !studentId || selectedOutOfStock) return
    setSubmitting(true)
    try {
      const request = await client.createLoanRequest({
        studentId,
        equipmentTypeId: selectedItem.equipment_type_id,
        quantity: REQUEST_QUANTITY,
      })
      setSubmitted({ name: selectedItem.name, quantity: request?.quantity ?? REQUEST_QUANTITY })
    } catch (error) {
      // FR-EQP-05 (T-15, T-16): 409 = อุปกรณ์ไม่พอ แจ้ง "ไม่สามารถยืมได้" เหตุอื่นแจ้งให้ลองใหม่ (Q-10)
      // แล้วโหลดจำนวนคงเหลือใหม่ ให้เห็นสถานะล่าสุด
      setSubmitted(null)
      setSubmitError(getErrorStatus(error) === 409 ? 'out_of_stock' : 'failed')
      try {
        const payload = await client.listEquipmentTypes()
        setItems(payload?.items ?? [])
      } catch {
        // คงรายการเดิมไว้ถ้าโหลดใหม่ไม่สำเร็จ
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <main className="mx-auto max-w-4xl p-4 md:p-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
          <h1 className="text-2xl font-bold text-slate-800">ยืมอุปกรณ์</h1>
          <div className="mt-4 rounded-2xl border border-sky-200 bg-sky-50 p-6 text-center text-sky-900" role="status">
            <b className="block text-xl">ส่งคำขอแล้ว</b>
            <small className="mt-1 block text-sm">รอเจ้าหน้าที่ตรวจสอบและอนุมัติ</small>
          </div>
          <div className="mt-3 flex justify-between gap-3 rounded-xl border border-slate-200 px-4 py-3 text-sm">
            <span className="text-slate-500">อุปกรณ์</span>
            <span>
              {submitted.name} × {submitted.quantity}
            </span>
          </div>
        </section>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-800">ยืมอุปกรณ์</h1>

        {/* ชั่วคราว: เลือกนักศึกษาตัวอย่าง จนกว่าจะมีล็อกอิน (คำตอบทีมข้อ 3 ใน tasks.md) */}
        <label htmlFor="equipment-student" className="mt-4 block text-sm text-slate-500">
          นักศึกษา
        </label>
        <select
          id="equipment-student"
          value={studentId}
          onChange={(event) => setStudentId(event.target.value)}
          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2"
        >
          {students.map((student) => (
            <option key={student.student_id} value={student.student_id}>
              {student.name} ({student.student_id})
            </option>
          ))}
        </select>

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
                  onClick={() => {
                    setSelectedId(item.equipment_type_id)
                    setSubmitError(null)
                  }}
                  aria-pressed={selected}
                  className={`flex w-full items-center justify-between gap-3 rounded-xl px-4 py-3 text-left transition ${
                    selected ? 'border-2 border-teal-700 bg-teal-50' : 'border border-slate-200 bg-white hover:bg-slate-50'
                  }`}
                >
                  <span>
                    <span className="block font-bold text-slate-800">{item.name}</span>
                    <span className="block text-sm text-slate-500">คงเหลือ {item.available_count}</span>
                  </span>
                  {item.available_count > 0 ? (
                    <span className="rounded-full bg-emerald-100 px-3 py-0.5 text-xs text-emerald-700">ว่าง</span>
                  ) : (
                    <span className="rounded-full bg-rose-100 px-3 py-0.5 text-xs text-rose-700">หมด</span>
                  )}
                </button>
              </li>
            )
          })}
        </ul>

        {selectedOutOfStock ? (
          <div className="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800" role="alert">
            <b className="block text-base">ไม่สามารถยืมได้</b>
            {selectedItem.name}หมดแล้ว กรุณาเลือกอุปกรณ์อื่น
          </div>
        ) : submitError ? (
          <div className="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800" role="alert">
            <b className="block text-base">
              {submitError === 'out_of_stock' ? 'ไม่สามารถยืมได้' : 'ส่งคำขอไม่สำเร็จ กรุณาลองใหม่'}
            </b>
          </div>
        ) : (
          <p className="mt-3 text-xs text-slate-500">เจ้าหน้าที่จะตรวจสอบและอนุมัติคำขอก่อนยืมเสมอ</p>
        )}
        <button
          type="button"
          onClick={submitRequest}
          disabled={!selectedItem || !studentId || selectedOutOfStock || submitting}
          className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white disabled:bg-slate-300"
        >
          ส่งคำขอยืม
        </button>
      </section>
    </main>
  )
}
