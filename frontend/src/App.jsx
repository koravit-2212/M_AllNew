import { useState } from 'react'

import BookDetailPage from './pages/BookDetailPage.jsx'
import SearchPage from './pages/SearchPage.jsx'

// FR-SRC-02, FR-SRC-03, AC-SRC-04
// App root ทำหน้าที่สลับระหว่าง Search Page และ Book Detail Page ตามการเลือกหนังสือ
export default function App() {
  const [selectedBookId, setSelectedBookId] = useState(null)

  if (selectedBookId) {
    return <BookDetailPage titleId={selectedBookId} onBack={() => setSelectedBookId(null)} />
  }

  return <SearchPage onSelectBook={setSelectedBookId} />
}
