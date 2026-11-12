import { useState } from 'react'

import BookDetailPage from './pages/BookDetailPage.jsx'
import SearchPage from './pages/SearchPage.jsx'
import SpaceBookingPage from './pages/SpaceBookingPage.jsx'

// FR-SRC-02, FR-SRC-03, AC-SRC-04: สลับระหว่าง Search Page และ Book Detail Page ตามการเลือกหนังสือ
// FR-BKG-01, NFR-USB-01: เมนูไปหน้าจองพื้นที่ (004-reserve) โดยไม่ลบหน้าเดิม
// แต่ละฟีเจอร์เพิ่มเมนูของตัวเอง 1 แถวใน MENUS และ 1 กรณีใน renderPage
const MENUS = [
  { key: 'books', label: 'หนังสือ' },
  { key: 'space-booking', label: 'จองพื้นที่' },
]

function BooksSection() {
  const [selectedBookId, setSelectedBookId] = useState(null)

  if (selectedBookId) {
    return <BookDetailPage titleId={selectedBookId} onBack={() => setSelectedBookId(null)} />
  }

  return <SearchPage onSelectBook={setSelectedBookId} />
}

function renderPage(menuKey) {
  switch (menuKey) {
    case 'space-booking':
      return <SpaceBookingPage />
    default:
      return <BooksSection />
  }
}

export default function App() {
  const [menuKey, setMenuKey] = useState(MENUS[0].key)

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="mx-auto flex max-w-4xl flex-wrap gap-2 px-4 pt-4 md:px-8" aria-label="เมนูหลัก">
        {MENUS.map((menu) => (
          <button
            key={menu.key}
            type="button"
            onClick={() => setMenuKey(menu.key)}
            aria-current={menuKey === menu.key ? 'page' : undefined}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
              menuKey === menu.key ? 'bg-teal-700 text-white' : 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-100'
            }`}
          >
            {menu.label}
          </button>
        ))}
      </nav>
      {renderPage(menuKey)}
    </div>
  )
}
