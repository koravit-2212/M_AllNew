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

test('test_TC_BKG_02_1_book_free_slot_success', async () => {
  // Given ช่วงเวลา 09.00–11.00 น. ของพื้นที่หนึ่งว่าง และผู้จองเป็นนักศึกษา
  const client = makeClient([space('A', 'พื้นที่ ก')])

  // When นักศึกษายืนยันการจอง
  await chooseAndConfirm(client, 'พื้นที่ ก', '09\\.00–11\\.00 น\\.')

  // Then (4) หน้าจอแสดงจองสำเร็จ พร้อมพื้นที่ วันที่ และเวลา
  await waitFor(() => expect(client.createReservation).toHaveBeenCalledWith({ userId: '64000001', spaceId: 'A', date: '2026-11-13', startTime: '09:00', endTime: '11:00' }))
  expect(await screen.findByText('จองสำเร็จ')).toBeTruthy()
  const card = within(screen.getByLabelText('รายละเอียดการจอง'))
  expect(card.getByText('พื้นที่ ก')).toBeTruthy()
  expect(card.getByText(/13 พ\.ย\. 2569/)).toBeTruthy()
  expect(card.getByText('09.00–11.00 น.')).toBeTruthy()
  // ((1)-(3) การตรวจความว่าง การบันทึก และข้อความจาก API ตรวจด้วย pytest)
})
