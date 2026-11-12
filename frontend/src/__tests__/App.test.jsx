// T-02 (FR-PRT-01, NFR-USB-01) งานพื้นฐาน: เมนูไปหน้าปริ้นเอกสารโดยไม่ลบหน้าเดิม
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import App from '../App.jsx'
import { api } from '../api/client.js'

vi.mock('../api/client.js', () => ({
  api: {
    searchBooks: vi.fn(),
  },
}))

test('T-02 กดเมนูปริ้นเอกสารแล้วเห็นหน้าปริ้นเอกสาร และกดเมนูหนังสือแล้วกลับหน้าค้นหาเดิม', async () => {
  api.searchBooks.mockResolvedValue({ results: [], page: 1, total: 0, partial: false })

  render(<App />)
  expect(screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeTruthy()

  fireEvent.click(screen.getByRole('button', { name: 'ปริ้นเอกสาร' }))
  expect(screen.getByRole('heading', { name: 'ปริ้นเอกสาร' })).toBeTruthy()
  expect(screen.queryByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeNull()

  fireEvent.click(screen.getByRole('button', { name: 'หนังสือ' }))
  await waitFor(() => {
    expect(screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeTruthy()
  })
})
