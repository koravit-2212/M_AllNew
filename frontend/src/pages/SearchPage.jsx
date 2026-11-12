import { useEffect, useState } from 'react'

import { api } from '../api/client.js'

// FR-SRC-01, FR-SRC-02, AC-SRC-01
// หน้าค้นหาหนังสือแบบ title-level ใช้ API /api/search เพื่อแสดงผลลัพธ์ที่ตรงกับคำค้น พร้อมสถานะสรุปต่อ title

const DEFAULT_QUERY = 'clean'
const PAGE_SIZE = 20

function formatAvailability(value) {
  switch (value) {
    case 'available':
      return { label: 'ว่าง', className: 'bg-emerald-100 text-emerald-700 border border-emerald-200' }
    case 'borrowed':
      return { label: 'ถูกยืม', className: 'bg-rose-100 text-rose-700 border border-rose-200' }
    case 'mixed':
      return { label: 'ผสม', className: 'bg-amber-100 text-amber-700 border border-amber-200' }
    default:
      return { label: 'ไม่พร้อม', className: 'bg-slate-100 text-slate-700 border border-slate-200' }
  }
}

export default function SearchPage({ onSelectBook = () => {} }) {
  const [query, setQuery] = useState(DEFAULT_QUERY)
  const [results, setResults] = useState([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [partial, setPartial] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadResults = async (nextQuery = query, nextPage = 1) => {
    const trimmedQuery = String(nextQuery ?? '').trim()
    if (!trimmedQuery) {
      setResults([])
      setPage(1)
      setTotal(0)
      setPartial(false)
      setError('')
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const payload = await api.searchBooks({ q: trimmedQuery, page: nextPage, per_page: PAGE_SIZE })
      const items = Array.isArray(payload?.results) ? payload.results : []
      const hasNoResults = items.length === 0
      const hasPartial = Boolean(payload?.partial)
      const message = payload?.message || (hasNoResults && !hasPartial ? 'ไม่พบข้อมูลหนังสือ' : '')

      setResults(items)
      setPage(payload?.page ?? nextPage)
      setTotal(payload?.total ?? 0)
      setPartial(hasPartial)
      setError(hasNoResults && !hasPartial ? message : '')
    } catch {
      setError('ไม่พบข้อมูลหนังสือ')
      setResults([])
      setTotal(0)
      setPartial(false)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadResults(DEFAULT_QUERY, 1)
  }, [])

  const handleSubmit = (event) => {
    event.preventDefault()
    void loadResults(query, 1)
  }

  const handleNextPage = () => {
    if (page * PAGE_SIZE < total) {
      void loadResults(query, page + 1)
    }
  }

  const handlePrevPage = () => {
    if (page > 1) {
      void loadResults(query, page - 1)
    }
  }

  const totalPages = total > 0 ? Math.max(1, Math.ceil(total / PAGE_SIZE)) : 1

  return (
    <main className="mx-auto max-w-4xl p-4 md:p-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-800">ค้นหาหนังสือ</h1>

        <form className="mt-5" onSubmit={handleSubmit}>
          <label className="mb-2 block text-sm font-medium text-slate-600" htmlFor="search-query">
            คำค้น (ชื่อหนังสือ / ผู้แต่ง / คำค้น / ISBN)
          </label>
          <div className="flex flex-col gap-3 md:flex-row">
            <input
              id="search-query"
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="ค้นหาหนังสือ / ผู้แต่ง / ISBN"
              className="flex-1 rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-base outline-none ring-0 transition focus:border-teal-500 focus:bg-white"
            />
            <button
              type="submit"
              className="rounded-xl bg-teal-700 px-5 py-3 font-semibold text-white transition hover:bg-teal-800"
            >
              ค้นหา
            </button>
          </div>
        </form>

        {partial && (
          <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
            <strong>แสดงผลลัพธ์บางส่วน</strong>
            <div className="mt-1">ฐานข้อมูลตอบช้า จึงแสดงเท่าที่ดึงมาได้แล้ว</div>
          </div>
        )}

        {loading && <div className="mt-4 text-sm text-slate-600">กำลังค้นหา...</div>}

        {!loading && results.length > 0 && (
          <div className="mt-5 space-y-3">
            <div className="text-sm text-slate-600">พบ {total} รายการ · หน้า {page}/{totalPages}</div>
            {results.map((book) => {
              const availability = formatAvailability(book.aggregated_availability)

              return (
                <button
                  type="button"
                  key={book.title_id || book.title}
                  onClick={() => onSelectBook(book.title_id)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 p-4 text-left shadow-sm transition hover:border-teal-300 hover:bg-slate-100"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-semibold text-slate-800">{book.title}</h2>
                      <p className="mt-1 text-sm text-slate-600">
                        {Array.isArray(book.authors) && book.authors.length > 0 ? book.authors.join(', ') : 'ไม่ระบุผู้แต่ง'}
                      </p>
                    </div>
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${availability.className}`}>
                      {availability.label}
                    </span>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-sm text-slate-600">
                    <span>{book.category || 'หนังสือทั่วไป'}</span>
                    <span>relevance: {book.relevance_score ?? 0}</span>
                  </div>
                </button>
              )
            })}

            {total > PAGE_SIZE && (
              <div className="mt-4 flex items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={handlePrevPage}
                  disabled={page <= 1}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
                >
                  ก่อนหน้า
                </button>
                <span className="text-sm text-slate-600">หน้า {page}</span>
                <button
                  type="button"
                  onClick={handleNextPage}
                  disabled={page >= totalPages}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
                >
                  ถัดไป
                </button>
              </div>
            )}
          </div>
        )}

        {!loading && error && (
          <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center text-amber-700">
            <div className="text-4xl">?</div>
            <div className="mt-2 text-xl font-semibold">{error}</div>
            <div className="mt-1 text-sm">ลองเปลี่ยนคำค้นอีกครั้ง</div>
          </div>
        )}
      </section>
    </main>
  )
}
