// T-02 (FR-EQP-01, NFR-USB-01) งานพื้นฐาน: เมนูไปหน้ายืมอุปกรณ์โดยไม่ลบหน้าเดิม
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import App from '../App.jsx'
import { api } from '../api/client.js'

vi.mock('../api/client.js', () => ({
  api: {
    searchBooks: vi.fn(),
  },
}))

test('T-02 กดเมนูยืมอุปกรณ์แล้วเห็นหน้ายืมอุปกรณ์ และกดเมนูหนังสือแล้วกลับหน้าค้นหาเดิม', async () => {
  api.searchBooks.mockResolvedValue({ results: [], page: 1, total: 0, partial: false })

  render(<App />)
  expect(screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeTruthy()

  fireEvent.click(screen.getByRole('button', { name: 'ยืมอุปกรณ์' }))
  expect(screen.getByRole('heading', { name: 'ยืมอุปกรณ์' })).toBeTruthy()
  expect(screen.queryByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeNull()

  fireEvent.click(screen.getByRole('button', { name: 'หนังสือ' }))
  await waitFor(() => {
    expect(screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeTruthy()
  })
})
