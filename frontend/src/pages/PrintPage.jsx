import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-PRT-01, FR-PRT-02, FR-PRT-03, NFR-USB-01
// หน้าปริ้นเอกสาร (UI-PRT-01) ขั้น 1 เลือกไฟล์และตัวเลือก ขั้น 2 ยืนยัน ขั้น 3 ผล
// FR-PRT-05: เครื่องพิมพ์ไม่พร้อม (409) แจ้งเตือนและให้ลองใหม่ ไฟล์ไม่รองรับเพิ่มใน T-10

const STEPS = ['1 เลือกไฟล์', '2 ยืนยัน', '3 ผล']

// UI-PRT-01: ขนาดไฟล์แบบ "1.2 MB"
function formatSize(bytes) {
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function Steps({ current }) {
  return (
    <ol className="mt-3 flex gap-2" aria-label="ขั้นตอนการพิมพ์">
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

function Row({ label, children }) {
  return (
    <div className="flex justify-between gap-3 py-1">
      <span className="text-slate-500">{label}</span>
      <span className="text-right">{children}</span>
    </div>
  )
}

// Q-05: จำนวนหน้าและจำนวนชุดต้องเป็นจำนวนเต็มตั้งแต่ 1
function toPositiveInt(value) {
  const n = Number(value)
  return Number.isInteger(n) && n >= 1 ? n : null
}

export default function PrintPage({ client = api }) {
  const [file, setFile] = useState(null)
  const [colorMode, setColorMode] = useState('BW')
  const [pagesInput, setPagesInput] = useState('1')
  const [copiesInput, setCopiesInput] = useState('1')
  const [options, setOptions] = useState(null)
  // step: 'select' | 'confirm' | 'done'
  const [step, setStep] = useState('select')
  const [job, setJob] = useState(null)
  // null | 'printer_not_ready' (409, FR-PRT-05) | 'failed' (Q-09)
  const [submitError, setSubmitError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const pages = toPositiveInt(pagesInput)
  const copies = toPositiveInt(copiesInput)

  // FR-PRT-01: เลือกไฟล์ ส่งข้อมูลไฟล์ไปหลังบ้าน (Q-07)
  const chooseFile = async (event) => {
    const picked = event.target.files?.[0]
    if (!picked) return
    setOptions(null)
    try {
      const uploaded = await client.uploadPrintFile({ filename: picked.name, contentType: picked.type, sizeBytes: picked.size })
      setFile({ id: uploaded.file_id, name: picked.name, size: picked.size })
    } catch {
      setFile(null)
    }
  }

  // FR-PRT-02: คำนวณค่าใช้บริการทุกครั้งที่เปลี่ยนตัวเลือก
  useEffect(() => {
    if (!file || !pages || !copies) {
      setOptions(null)
      return undefined
    }
    let active = true
    client
      .getPrintOptions({ fileId: file.id, pages, copies, colorMode })
      .then((payload) => active && setOptions(payload))
      .catch(() => active && setOptions(null))
    return () => {
      active = false
    }
  }, [client, file, pages, copies, colorMode])

  // FR-PRT-03: ยืนยันการพิมพ์ ส่งงานไปเครื่องปริ้นและบันทึกการใช้บริการ
  const submit = async () => {
    if (!file || !options) return
    setSubmitting(true)
    setSubmitError(null)
    try {
      const result = await client.submitPrintJob({ fileId: file.id, pages: options.pages, copies: options.copies, colorMode: options.color_mode })
      setJob({ ...result, filename: result.filename || file.name })
      setStep('done')
    } catch (error) {
      setSubmitError(error?.status === 409 ? 'printer_not_ready' : 'failed')
    } finally {
      setSubmitting(false)
    }
  }

  if (step === 'confirm' && submitError === 'printer_not_ready') {
    return (
      <main className="mx-auto max-w-4xl p-4 md:p-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
          <h1 className="text-2xl font-bold text-slate-800">ปริ้นเอกสาร</h1>
          <Steps current={2} />
          <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 p-6 text-center text-rose-900" role="alert">
            <b className="block text-xl">เครื่องพิมพ์ไม่พร้อมใช้งาน</b>
            <small className="mt-1 block text-sm">ยังไม่ได้ส่งงานพิมพ์ กรุณาลองใหม่หรือติดต่อเจ้าหน้าที่</small>
          </div>
          <button
            type="button"
            onClick={submit}
            disabled={submitting}
            className="mt-4 w-full rounded-xl border border-teal-700 bg-white px-4 py-3 font-bold text-teal-700 disabled:opacity-50"
          >
            ลองใหม่
          </button>
        </section>
      </main>
    )
  }

  if (step === 'done' && job) {
    return (
      <main className="mx-auto max-w-4xl p-4 md:p-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
          <h1 className="text-2xl font-bold text-slate-800">ปริ้นเอกสาร</h1>
          <Steps current={2} />
          <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center text-emerald-900" role="status">
            <b className="block text-xl">ส่งงานพิมพ์แล้ว</b>
            <small className="mt-1 block text-sm">บันทึกข้อมูลการใช้บริการแล้ว</small>
          </div>
          <div className="mt-3 rounded-xl border border-slate-200 px-4 py-3 text-sm" aria-label="งานพิมพ์">
            <Row label="ไฟล์">{job.filename}</Row>
            <Row label="จำนวน">{job.total_pages} หน้า</Row>
            <Row label="ค่าใช้บริการ">{job.total_cost} บาท</Row>
          </div>
        </section>
      </main>
    )
  }

  if (step === 'confirm' && file && options) {
    return (
      <main className="mx-auto max-w-4xl p-4 md:p-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
          <h1 className="text-2xl font-bold text-slate-800">ปริ้นเอกสาร</h1>
          <Steps current={1} />
          {submitError === 'failed' && (
            <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800" role="alert">
              <b className="block text-base">ส่งงานพิมพ์ไม่สำเร็จ กรุณาลองใหม่</b>
            </div>
          )}
          <div className="mt-3 rounded-xl border border-slate-200 px-4 py-3 text-sm" aria-label="งานพิมพ์">
            <Row label="ไฟล์">{file.name}</Row>
            <Row label="จำนวน">{options.total_pages} หน้า</Row>
            <Row label="ค่าใช้บริการ">{options.estimated_cost} บาท</Row>
          </div>
          <button
            type="button"
            onClick={submit}
            disabled={submitting}
            className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white disabled:bg-slate-300"
          >
            ยืนยันการพิมพ์
          </button>
          <button
            type="button"
            onClick={() => {
              setStep('select')
              setSubmitError(null)
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
        <h1 className="text-2xl font-bold text-slate-800">ปริ้นเอกสาร</h1>
        <Steps current={0} />

        <label htmlFor="print-file" className="mt-4 block text-sm text-slate-500">
          ไฟล์
        </label>
        <input id="print-file" type="file" onChange={chooseFile} className="mt-1 block w-full text-sm" />
        {file && (
          <p className="mt-1 text-sm text-slate-700">
            {file.name} ({formatSize(file.size)})
          </p>
        )}

        {options && (
          <fieldset className="mt-4">
            <legend className="text-sm text-slate-500">ชนิดการพิมพ์</legend>
            {options.allowed_color_modes.map((mode) => (
              <label key={mode.code} className="mt-2 flex items-center gap-2 text-sm">
                <input
                  type="radio"
                  name="color-mode"
                  value={mode.code}
                  checked={colorMode === mode.code}
                  onChange={() => setColorMode(mode.code)}
                />
                {mode.label}
              </label>
            ))}
          </fieldset>
        )}

        <label htmlFor="print-pages" className="mt-4 block text-sm text-slate-500">
          จำนวนหน้า
        </label>
        <input
          id="print-pages"
          type="number"
          min="1"
          value={pagesInput}
          onChange={(event) => setPagesInput(event.target.value)}
          className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
        />
        <label htmlFor="print-copies" className="mt-4 block text-sm text-slate-500">
          จำนวนชุด
        </label>
        <input
          id="print-copies"
          type="number"
          min="1"
          value={copiesInput}
          onChange={(event) => setCopiesInput(event.target.value)}
          className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
        />

        {options && (
          <div className="mt-4 rounded-xl border border-slate-200 px-4 py-3 text-sm" aria-label="ค่าใช้บริการ">
            <Row label="คำนวณ">
              {options.pages} หน้า × {options.copies} ชุด = {options.total_pages} หน้า
            </Row>
            <Row label="ค่าใช้บริการ">{options.estimated_cost} บาท</Row>
          </div>
        )}

        <button
          type="button"
          onClick={() => setStep('confirm')}
          disabled={!file || !options}
          className="mt-4 w-full rounded-xl bg-teal-700 px-4 py-3 font-bold text-white disabled:bg-slate-300"
        >
          ถัดไป
        </button>
      </section>
    </main>
  )
}
