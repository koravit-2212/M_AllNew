import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import App from '../App.jsx'
import { api } from '../api/client.js'

vi.mock('../api/client.js', () => ({
  api: {
    searchBooks: vi.fn(),
    getBookDetail: vi.fn(),
  },
}))

test('Book Detail Page แสดงข้อมูลหนังสือและสถานะรายเล่มเมื่อเลือกหนังสือจาก Search Page', async () => {
  api.searchBooks.mockResolvedValue({
    results: [
      {
        title_id: 'bk-clean-code',
        title: 'Clean Code',
        authors: ['Robert C. Martin'],
        category: 'วิศวกรรมซอฟต์แวร์',
        aggregated_availability: 'mixed',
        relevance_score: 90,
      },
    ],
    page: 1,
    total: 1,
    partial: false,
  })

  api.getBookDetail.mockResolvedValue({
    title_id: 'bk-clean-code',
    title: 'Clean Code',
    authors: ['Robert C. Martin'],
    isbn: '9780132350884',
    call_number: 'QA76.76 .M37',
    category: 'วิศวกรรมซอฟต์แวร์',
    aggregated_availability: 'mixed',
    copies: [
      { copy_id: 'CC-001', status: 'available', shelf_location: 'ชั้น 3', location_detail: 'โซน B' },
      { copy_id: 'CC-002', status: 'borrowed', shelf_location: 'ชั้น 3', location_detail: 'โซน B' },
      { copy_id: 'CC-003', status: 'available', shelf_location: 'ชั้น 3', location_detail: 'โซน B' },
    ],
  })

  render(<App />)

  const input = screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')
  fireEvent.change(input, { target: { value: 'clean' } })
  fireEvent.click(screen.getByRole('button', { name: 'ค้นหา' }))

  await waitFor(() => {
    expect(screen.getByText('Clean Code')).toBeTruthy()
  })

  fireEvent.click(screen.getByText('Clean Code'))

  await waitFor(() => {
    expect(screen.getByText('รายละเอียดหนังสือ')).toBeTruthy()
  })

  expect(screen.getByText('Robert C. Martin')).toBeTruthy()
  expect(screen.getByText('QA76.76 .M37')).toBeTruthy()
  expect(screen.getByText('9780132350884')).toBeTruthy()
  expect(screen.getAllByText('ว่าง').length).toBeGreaterThan(0)
  expect(screen.getAllByText('ถูกยืม').length).toBeGreaterThan(0)
  expect(screen.getAllByText(/ชั้น 3/).length).toBeGreaterThan(0)
})
