// T-02 ของ 004 (FR-BKG-01), 006 (FR-PRT-01), 007 (FR-EQP-01) และ NFR-USB-01 งานพื้นฐาน:
// แต่ละเมนูไปหน้าของฟีเจอร์นั้นโดยไม่ลบหน้าเดิม และกดเมนู "หนังสือ" แล้วกลับหน้าค้นหาเดิม
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import App from '../App.jsx'
import { api } from '../api/client.js'

vi.mock('../api/client.js', () => ({
  api: {
    searchBooks: vi.fn(),
  },
}))

const FEATURE_MENUS = [
  ['จองพื้นที่', 'จองพื้นที่ในห้องสมุด'],
  ['ปริ้นเอกสาร', 'ปริ้นเอกสาร'],
  ['ยืมอุปกรณ์', 'ยืมอุปกรณ์'],
  ['อนุมัติยืมอุปกรณ์ (เจ้าหน้าที่)', 'อนุมัติคำขอยืมอุปกรณ์ (เจ้าหน้าที่)'],
]

test.each(FEATURE_MENUS)('T-02 กดเมนู %s แล้วเห็นหัวข้อ %s และกดเมนูหนังสือแล้วกลับหน้าค้นหาเดิม', async (menu, heading) => {
  api.searchBooks.mockResolvedValue({ results: [], page: 1, total: 0, partial: false })

  render(<App />)
  expect(screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeTruthy()

  fireEvent.click(screen.getByRole('button', { name: menu }))
  expect(screen.getByRole('heading', { name: heading })).toBeTruthy()
  expect(screen.queryByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeNull()

  fireEvent.click(screen.getByRole('button', { name: 'หนังสือ' }))
  await waitFor(() => {
    expect(screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeTruthy()
  })
})
