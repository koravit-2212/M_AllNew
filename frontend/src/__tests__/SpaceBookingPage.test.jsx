// T-04 (FR-BKG-01, NFR-USB-01) ตรวจด้วย AC-BKG-01
import { fireEvent, render, screen, within } from '@testing-library/react'
import { vi } from 'vitest'

import SpaceBookingPage from '../pages/SpaceBookingPage.jsx'

export const SPACES = [
  {
    space_id: 'A',
    space_type: 'โซน',
    facility_name: 'พื้นที่ทดสอบ 1',
    available: true,
    slots: [
      { slot_id: 'A1', date: '2026-11-13', start_time: '09:00', end_time: '11:00', available: true },
      { slot_id: 'A2', date: '2026-11-13', start_time: '11:00', end_time: '13:00', available: false },
    ],
  },
  {
    space_id: 'B',
    space_type: 'ห้อง',
    facility_name: 'พื้นที่ทดสอบเต็ม',
    available: false,
    slots: [{ slot_id: 'B1', date: '2026-11-13', start_time: '09:00', end_time: '11:00', available: false }],
  },
]

function makeClient() {
  return { listAvailableSpaces: vi.fn().mockResolvedValue({ spaces: SPACES }) }
}

describe('AC-BKG-01 แสดงพื้นที่ที่ใช้งานได้พร้อมช่วงเวลา', () => {
  it('AC-BKG-01 เห็นพื้นที่ สถานะว่าง/เต็ม และเลือกพื้นที่แล้วเห็นช่วงเวลาให้เลือก', async () => {
    // Given มีพื้นที่เปิดให้บริการในระบบ
    const client = makeClient()

    // When นักศึกษาเลือกบริการพื้นที่
    render(<SpaceBookingPage client={client} />)

    // Then ระบบแสดงรายการพื้นที่ที่ใช้งานได้พร้อมช่วงเวลาให้เลือก
    const open = await screen.findByRole('button', { name: /พื้นที่ทดสอบ 1/ })
    expect(screen.getByText('พื้นที่ที่ใช้งานได้')).toBeTruthy()
    expect(within(open).getByText('ว่าง')).toBeTruthy()
    expect(within(open).getByText('ว่างวันนี้')).toBeTruthy()
    const full = screen.getByRole('button', { name: /พื้นที่ทดสอบเต็ม/ })
    expect(within(full).getByText('เต็ม')).toBeTruthy()
    expect(full.disabled).toBe(true)

    fireEvent.click(open)
    expect(screen.getByText('ช่วงเวลา')).toBeTruthy()
    const freeSlot = screen.getByRole('button', { name: /09\.00–11\.00 น\./ })
    const fullSlot = screen.getByRole('button', { name: /11\.00–13\.00 น\./ })
    expect(within(freeSlot).getByText('ว่าง')).toBeTruthy()
    expect(fullSlot.disabled).toBe(true)
    fireEvent.click(freeSlot)
    expect(freeSlot.getAttribute('aria-pressed')).toBe('true')
  })
})
