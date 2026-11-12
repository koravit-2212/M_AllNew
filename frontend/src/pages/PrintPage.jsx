import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-PRT-01, FR-PRT-02, NFR-USB-01
// หน้าปริ้นเอกสาร (UI-PRT-01) ขั้น 1 เลือกไฟล์ ชนิดการพิมพ์ จำนวนหน้า จำนวนชุด และเห็นค่าใช้บริการ
// ขั้นยืนยันและผลเพิ่มใน T-06 เครื่องพิมพ์ไม่พร้อมเพิ่มใน T-08 ไฟล์ไม่รองรับเพิ่มใน T-10

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
      </section>
    </main>
  )
}
