import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-SRC-02, FR-SRC-03, AC-SRC-04
// หน้ารายละเอียดหนังสือแสดงฟิลด์ขั้นต่ำและสถานะ per-copy พร้อมตำแหน่งจัดเก็บตาม mockup UI-SRC-02

function formatCopyStatus(status) {
  switch (status) {
    case 'available':
      return { label: 'ว่าง', className: 'bg-emerald-100 text-emerald-700 border border-emerald-200' }
    case 'borrowed':
      return { label: 'ถูกยืม', className: 'bg-rose-100 text-rose-700 border border-rose-200' }
    case 'reserved':
      return { label: 'จอง', className: 'bg-amber-100 text-amber-700 border border-amber-200' }
    default:
      return { label: 'ไม่พร้อม', className: 'bg-slate-100 text-slate-700 border border-slate-200' }
  }
}

export default function BookDetailPage({ titleId, onBack = () => {} }) {
  const [book, setBook] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let ignore = false

    async function loadBook() {
      setLoading(true)
      setError('')

      try {
        const payload = await api.getBookDetail(titleId)
        if (!ignore) {
          setBook(payload)
        }
      } catch {
        if (!ignore) {
          setError('ไม่สามารถโหลดรายละเอียดหนังสือได้')
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    void loadBook()

    return () => {
      ignore = true
    }
  }, [titleId])

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl p-4 md:p-8">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 text-slate-600">กำลังโหลดรายละเอียดหนังสือ...</div>
      </main>
    )
  }

  if (error || !book) {
    return (
      <main className="mx-auto max-w-3xl p-4 md:p-8">
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-rose-700">
          <div className="text-lg font-semibold">{error || 'ไม่พบรายละเอียดหนังสือ'}</div>
          <button
            type="button"
            onClick={onBack}
            className="mt-4 rounded-xl bg-slate-700 px-4 py-2 text-sm font-medium text-white"
          >
            กลับไปยังรายการ
          </button>
        </div>
      </main>
    )
  }

  const availableCount = book.copies.filter((copy) => copy.status === 'available').length
  const totalCopies = book.copies.length

  return (
    <main className="mx-auto max-w-3xl p-4 md:p-8">
      <div className="mb-4">
        <button
          type="button"
          onClick={onBack}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
        >
          ← กลับ
        </button>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-800">รายละเอียดหนังสือ</h1>

        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex flex-col gap-2 text-sm md:flex-row md:items-center md:justify-between">
            <span className="text-slate-500">ชื่อ</span>
            <span className="font-semibold text-slate-800">{book.title}</span>
          </div>
          <div className="mt-2 flex flex-col gap-2 text-sm md:flex-row md:items-center md:justify-between">
            <span className="text-slate-500">ผู้แต่ง</span>
            <span className="font-medium text-slate-700">{book.authors.join(', ')}</span>
          </div>
          <div className="mt-2 flex flex-col gap-2 text-sm md:flex-row md:items-center md:justify-between">
            <span className="text-slate-500">เลขเรียกหนังสือ</span>
            <span className="font-medium text-slate-700">{book.call_number}</span>
          </div>
          <div className="mt-2 flex flex-col gap-2 text-sm md:flex-row md:items-center md:justify-between">
            <span className="text-slate-500">ISBN</span>
            <span className="font-medium text-slate-700">{book.isbn}</span>
          </div>
          <div className="mt-2 flex flex-col gap-2 text-sm md:flex-row md:items-center md:justify-between">
            <span className="text-slate-500">หมวดหมู่</span>
            <span className="font-medium text-slate-700">{book.category}</span>
          </div>
          <div className="mt-2 flex flex-col gap-2 text-sm md:flex-row md:items-center md:justify-between">
            <span className="text-slate-500">สถานะรวม</span>
            <span className="font-medium text-slate-700">ว่าง {availableCount} จาก {totalCopies} เล่ม</span>
          </div>
        </div>

        <div className="mt-6">
          <h2 className="text-lg font-semibold text-slate-800">สถานะรายเล่ม (per-copy) และตำแหน่งจัดเก็บ</h2>

          <div className="mt-3 space-y-3">
            {book.copies.map((copy, index) => {
              const status = formatCopyStatus(copy.status)

              return (
                <div key={copy.copy_id || index} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-semibold text-slate-800">เล่ม {index + 1}</div>
                      <div className="mt-1 text-sm text-slate-500">{copy.shelf_location} {copy.location_detail}</div>
                    </div>
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${status.className}`}>
                      {status.label}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>
    </main>
  )
}
