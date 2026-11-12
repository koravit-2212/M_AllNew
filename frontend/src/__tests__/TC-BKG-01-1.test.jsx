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

test('test_TC_BKG_01_1_list_open_spaces_with_slots', async () => {
  // Given มีพื้นที่เปิดให้บริการ 3 แห่ง แต่ละแห่งมีช่วงเวลา 4 ช่วงที่ยังไม่มีใครจอง
  const client = makeClient([space('A', 'พื้นที่ ก'), space('B', 'พื้นที่ ข'), space('C', 'พื้นที่ ค')])

  // When นักศึกษาเลือกบริการพื้นที่ แล้วเลือกพื้นที่ 1 แห่ง
  render(<SpaceBookingPage client={client} />)
  const first = await screen.findByRole('button', { name: /พื้นที่ ก/ })

  // Then (2) แสดงชื่อพื้นที่ทุกแห่งพร้อมสถานะว่าง
  for (const name of ['พื้นที่ ก', 'พื้นที่ ข', 'พื้นที่ ค']) {
    expect(within(screen.getByRole('button', { name: new RegExp(name) })).getByText('ว่าง')).toBeTruthy()
  }
  // (3) เลือกพื้นที่แล้วเห็นช่วงเวลาให้เลือก
  fireEvent.click(first)
  for (const label of ['09.00–11.00 น.', '11.00–13.00 น.', '13.00–15.00 น.', '15.00–17.00 น.']) {
    expect(screen.getByRole('button', { name: new RegExp(label.replace(/\./g, '\\.')) }).disabled).toBe(false)
  }
  // ((1) ข้อมูลจาก API ตรวจด้วย pytest)
})
