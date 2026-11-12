import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import SearchPage from '../pages/SearchPage.jsx'
import { api } from '../api/client.js'

describe('AC-SRC-01 Search Page', () => {
  it('calls the search API for a partial match and shows matching results', async () => {
    vi.spyOn(api, 'searchBooks').mockResolvedValue({
      query: 'clean',
      page: 1,
      per_page: 20,
      total: 2,
      results: [
        {
          title: 'Clean Code',
          authors: ['Robert C. Martin'],
          aggregated_availability: 'available',
          relevance_score: 90,
        },
        {
          title: 'Clean Architecture',
          authors: ['Robert C. Martin'],
          aggregated_availability: 'borrowed',
          relevance_score: 75,
        },
      ],
    })

    render(<SearchPage />)

    const input = screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')
    expect(input.value).toBe('clean')

    fireEvent.change(input, { target: { value: 'clean' } })
    fireEvent.click(screen.getByRole('button', { name: /ค้นหา/i }))

    await waitFor(() => {
      expect(api.searchBooks).toHaveBeenCalledWith({ q: 'clean', page: 1, per_page: 20 })
    })

    expect(await screen.findByText('Clean Code')).toBeTruthy()
    expect(screen.getByText('ว่าง')).toBeTruthy()
  })

  it('shows the no-result message when the API returns no books', async () => {
    vi.spyOn(api, 'searchBooks').mockResolvedValue({
      query: 'xyzqwe',
      page: 1,
      per_page: 20,
      total: 0,
      results: [],
      message: 'ไม่พบข้อมูลหนังสือ',
    })

    render(<SearchPage />)

    const input = screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')
    fireEvent.change(input, { target: { value: 'xyzqwe' } })
    fireEvent.click(screen.getByRole('button', { name: /ค้นหา/i }))

    expect(await screen.findByText('ไม่พบข้อมูลหนังสือ')).toBeTruthy()
    expect(screen.queryByText('Clean Code')).toBeNull()
  })

  it('shows the partial results alert while still rendering the usable results', async () => {
    vi.spyOn(api, 'searchBooks').mockResolvedValue({
      query: 'clean',
      page: 1,
      per_page: 20,
      total: 2,
      partial: true,
      results: [
        {
          title: 'Clean Code',
          authors: ['Robert C. Martin'],
          category: 'วิศวกรรมซอฟต์แวร์',
          aggregated_availability: 'available',
          relevance_score: 90,
        },
      ],
    })

    render(<SearchPage />)

    const input = screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')
    fireEvent.change(input, { target: { value: 'clean' } })
    fireEvent.click(screen.getByRole('button', { name: /ค้นหา/i }))

    expect(await screen.findByText('แสดงผลลัพธ์บางส่วน')).toBeTruthy()
    expect(screen.getByText('ฐานข้อมูลตอบช้า จึงแสดงเท่าที่ดึงมาได้แล้ว')).toBeTruthy()
    expect(screen.getByText('Clean Code')).toBeTruthy()
  })

  it('shows the database unavailable fallback when the API reports the library DB is down', async () => {
    vi.spyOn(api, 'searchBooks').mockResolvedValue({
      query: 'clean',
      page: 1,
      per_page: 20,
      total: 0,
      partial: false,
      results: [],
      message: 'ฐานข้อมูลหนังสือไม่พร้อมใช้งาน',
    })

    render(<SearchPage />)

    const input = screen.getByPlaceholderText('ค้นหาหนังสือ / ผู้แต่ง / ISBN')
    fireEvent.change(input, { target: { value: 'clean' } })
    fireEvent.click(screen.getByRole('button', { name: /ค้นหา/i }))

    expect(await screen.findByText('ฐานข้อมูลหนังสือไม่พร้อมใช้งาน')).toBeTruthy()
    expect(screen.queryByText('Clean Code')).toBeNull()
    expect(screen.queryByText('แสดงผลลัพธ์บางส่วน')).toBeNull()
  })
})
