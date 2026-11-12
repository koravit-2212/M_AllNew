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

test('test_TC_BKG_02_3_ineligible_user_rejected', async () => {
  // Given ช่วงเวลาว่าง แต่ผู้จองไม่ใช่นักศึกษา บุคลากร หรือผู้ได้รับอนุญาต (หลังบ้านตอบ 403)
  const client = makeClient([space('A', 'พื้นที่ ก')], vi.fn().mockRejectedValue(Object.assign(new Error('Reservation failed: 403'), { status: 403 })))

  // When ผู้ใช้นั้นยืนยันการจอง
  await chooseAndConfirm(client, 'พื้นที่ ก', '09\\.00–11\\.00 น\\.', 'GU-0001')

  // Then (3) หน้าจอแสดงว่าไม่มีสิทธิ์จองพื้นที่ และไม่แสดงว่าจองสำเร็จ
  expect(await screen.findByText('ไม่มีสิทธิ์จองพื้นที่')).toBeTruthy()
  expect(screen.queryByText('จองสำเร็จ')).toBeNull()
  // ((1)(2) ตรวจด้วย pytest)
})
