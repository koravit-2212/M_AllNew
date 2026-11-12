// test ตรวจว่า Search Page เปิดใช้งานได้หลังจาก task T-04
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import App from '../App.jsx'
import { api } from '../api/client.js'

vi.mock('../api/client.js', () => ({
  api: {
    searchBooks: vi.fn(),
  },
}))

test('Search Page เปิดได้', async () => {
  api.searchBooks.mockResolvedValue({
    results: [
      {
        title_id: 't-1',
        title: 'Clean Code',
        authors: ['Robert C. Martin'],
        category: 'Programming',
        aggregated_availability: 'available',
        relevance_score: 90,
      },
    ],
    page: 1,
    total: 1,
    partial: false,
  })

  render(<App />)

  await waitFor(() => {
    expect(screen.getByText('ค้นหาหนังสือ')).toBeTruthy()
  })
  expect(screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')).toBeTruthy()
})

test('Search Page แสดงข้อความไม่พบข้อมูลหนังสือเมื่อไม่มีผลลัพธ์', async () => {
  api.searchBooks.mockResolvedValue({
    results: [],
    page: 1,
    total: 0,
    partial: false,
    message: 'ไม่พบข้อมูลหนังสือ',
  })

  render(<App />)

  const input = screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')
  fireEvent.change(input, { target: { value: 'xyzqwe' } })
  fireEvent.click(screen.getByRole('button', { name: 'ค้นหา' }))

  await waitFor(() => {
    expect(screen.getAllByText('ไม่พบข้อมูลหนังสือ').length).toBeGreaterThan(0)
  })
})
