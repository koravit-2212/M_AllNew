import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import SpaceBookingPage from '../pages/SpaceBookingPage.jsx'

// test จาก specs/004-reserve/test-cases.md ห้ามแก้ให้ผ่าน
function slots(prefix, bookedStarts = []) {
  return [
    ['09:00', '11:00'],
    ['11:00', '13:00'],
    ['13:00', '15:00'],
    ['15:00', '17:00'],
  ].map(([start, end]) => ({
    slot_id: `${prefix}-${start}`,
    date: '2026-11-13',
    start_time: start,
    end_time: end,
    available: !bookedStarts.includes(start),
  }))
}

function space(id, name, bookedStarts = []) {
  const list = slots(id, bookedStarts)
  return { space_id: id, space_type: 'โซน', facility_name: name, available: list.some((s) => s.available), slots: list }
}

const USERS = [
  { userId: '64000001', name: 'นักศึกษาทดสอบ', userType: 'student' },
  { userId: 'GU-0001', name: 'บุคคลภายนอกทดสอบ', userType: 'guest' },
]

function makeClient(spaces, createReservation = vi.fn().mockResolvedValue({ reservationId: 'RSV-0001', status: 'confirmed', message: 'จองสำเร็จ' })) {
  return {
    listAvailableSpaces: vi.fn().mockResolvedValue({ spaces }),
    listSpaceUsers: vi.fn().mockResolvedValue({ items: USERS }),
    createReservation,
  }
}

async function chooseAndConfirm(client, spaceName, slotLabel, userId = '64000001') {
  render(<SpaceBookingPage client={client} />)
  fireEvent.click(await screen.findByRole('button', { name: new RegExp(spaceName) }))
  await screen.findByRole('option', { name: /บุคคลภายนอกทดสอบ/ })
  fireEvent.change(screen.getByLabelText('ผู้จอง'), { target: { value: userId } })
  fireEvent.click(screen.getByRole('button', { name: new RegExp(slotLabel) }))
  fireEvent.click(screen.getByRole('button', { name: 'ถัดไป' }))
  fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการจอง' }))
}

test('test_TC_BKG_01_2_fully_booked_space_marked_full', async () => {
  // Given พื้นที่ 1 แห่งถูกจองครบทุกช่วง ส่วนพื้นที่อื่นว่างทุกช่วง
  const client = makeClient([space('A', 'พื้นที่เต็ม', ['09:00', '11:00', '13:00', '15:00']), space('B', 'พื้นที่ว่าง', ['11:00'])])

  // When นักศึกษาเลือกบริการพื้นที่
  render(<SpaceBookingPage client={client} />)
  const full = await screen.findByRole('button', { name: /พื้นที่เต็ม/ })

  // Then (1) พื้นที่ที่ว่าง 0 ช่วงขึ้นเต็ม พื้นที่อื่นขึ้นว่าง
  expect(within(full).getByText('เต็ม')).toBeTruthy()
  const open = screen.getByRole('button', { name: /พื้นที่ว่าง/ })
  expect(within(open).getByText('ว่าง')).toBeTruthy()
  // (2) เลือกพื้นที่ที่เต็มไม่ได้ และช่วงที่ถูกจองแล้วเลือกไม่ได้
  expect(full.disabled).toBe(true)
  fireEvent.click(open)
  expect(screen.getByRole('button', { name: /11\.00–13\.00 น\./ }).disabled).toBe(true)
  expect(screen.getByRole('button', { name: /09\.00–11\.00 น\./ }).disabled).toBe(false)
})
