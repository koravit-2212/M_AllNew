// T-04 (FR-BKG-01, NFR-USB-01) ตรวจด้วย AC-BKG-01
// T-06 (FR-BKG-03, NFR-USB-01) ตรวจด้วย AC-BKG-02
// T-08 (FR-BKG-04, NFR-USB-01) ตรวจด้วย AC-BKG-03
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import SpaceBookingPage from '../pages/SpaceBookingPage.jsx'

const SPACES = [
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

const USERS = [
  { userId: 'U1', name: 'ผู้ใช้ทดสอบ 1', userType: 'student' },
  { userId: 'U2', name: 'ผู้ใช้ทดสอบ 2', userType: 'guest' },
]

function makeClient(createReservation = vi.fn().mockResolvedValue({ reservationId: 'RSV-0001', status: 'confirmed', message: 'จองสำเร็จ' })) {
  return {
    listAvailableSpaces: vi.fn().mockResolvedValue({ spaces: SPACES }),
    listSpaceUsers: vi.fn().mockResolvedValue({ items: USERS }),
    createReservation,
  }
}

async function goToConfirm(client, user = 'U1') {
  render(<SpaceBookingPage client={client} />)
  fireEvent.click(await screen.findByRole('button', { name: /พื้นที่ทดสอบ 1/ }))
  await screen.findByRole('option', { name: /ผู้ใช้ทดสอบ 2/ })
  fireEvent.change(screen.getByLabelText('ผู้จอง'), { target: { value: user } })
  fireEvent.click(screen.getByRole('button', { name: /09\.00–11\.00 น\./ }))
  fireEvent.click(screen.getByRole('button', { name: 'ถัดไป' }))
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

describe('AC-BKG-02 จองสำเร็จ', () => {
  it('AC-BKG-02 กดถัดไป ยืนยันการจอง แล้วเห็นจองสำเร็จพร้อมพื้นที่ วันที่ และเวลา', async () => {
    // Given มีพื้นที่ว่างในช่วงเวลาที่นักศึกษาเลือก
    const client = makeClient()
    await goToConfirm(client)
    const card = within(screen.getByLabelText('รายละเอียดการจอง'))
    expect(card.getByText('พื้นที่ทดสอบ 1')).toBeTruthy()

    // When นักศึกษายืนยันการจอง
    fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการจอง' }))

    // Then ระบบบันทึกการจองและแจ้งผลสำเร็จ
    await waitFor(() =>
      expect(client.createReservation).toHaveBeenCalledWith({ userId: 'U1', spaceId: 'A', date: '2026-11-13', startTime: '09:00', endTime: '11:00' }),
    )
    expect(await screen.findByText('จองสำเร็จ')).toBeTruthy()
    expect(screen.getByText('บันทึกการจองแล้ว')).toBeTruthy()
    const result = within(screen.getByLabelText('รายละเอียดการจอง'))
    expect(result.getByText('พื้นที่ทดสอบ 1')).toBeTruthy()
    expect(result.getByText(/13 พ\.ย\. 2569/)).toBeTruthy()
    expect(result.getByText('09.00–11.00 น.')).toBeTruthy()

    // กลับหน้าหลักแล้วโหลดสถานะใหม่
    fireEvent.click(screen.getByRole('button', { name: 'กลับหน้าหลัก' }))
    await waitFor(() => expect(client.listAvailableSpaces).toHaveBeenCalledTimes(2))
  })

  it('AC-BKG-02 ผู้ไม่มีสิทธิ์ (403) เห็นไม่มีสิทธิ์จองพื้นที่ (CON-ELG-01, Q-01)', async () => {
    const client = makeClient(vi.fn().mockRejectedValue(Object.assign(new Error('Reservation failed: 403'), { status: 403 })))
    await goToConfirm(client, 'U2')
    fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการจอง' }))
    expect(await screen.findByText('ไม่มีสิทธิ์จองพื้นที่')).toBeTruthy()
    expect(screen.queryByText('จองสำเร็จ')).toBeNull()
  })

  it('AC-BKG-02 เหตุอื่น (เช่น เน็ตหลุด) เห็นจองไม่สำเร็จ กรุณาลองใหม่ (Q-04)', async () => {
    const client = makeClient(vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    await goToConfirm(client)
    fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการจอง' }))
    expect(await screen.findByText('จองไม่สำเร็จ กรุณาลองใหม่')).toBeTruthy()
    expect(screen.getByRole('button', { name: 'ยืนยันการจอง' })).toBeTruthy()
  })
})

describe('AC-BKG-03 พื้นที่ไม่ว่าง', () => {
  it('AC-BKG-03 ยืนยันแล้วหลังบ้านตอบ 409 เห็นพื้นที่ไม่ว่างในช่วงเวลานี้ และกลับไปเลือกใหม่ได้', async () => {
    // Given พื้นที่ที่เลือกไม่ว่างในช่วงเวลานั้น (มีคนจองไปก่อน)
    const client = makeClient(vi.fn().mockRejectedValue(Object.assign(new Error('Reservation failed: 409'), { status: 409 })))
    await goToConfirm(client)

    // When นักศึกษาพยายามจอง
    fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการจอง' }))

    // Then ระบบแจ้งให้เลือกพื้นที่หรือเวลาอื่น
    expect(await screen.findByText('พื้นที่ไม่ว่างในช่วงเวลานี้')).toBeTruthy()
    expect(screen.getByText(/กรุณาเลือกพื้นที่หรือเวลาอื่น/)).toBeTruthy()
    expect(screen.queryByText('จองสำเร็จ')).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: 'กลับไปเลือกพื้นที่/เวลาใหม่' }))
    expect(await screen.findByText('พื้นที่ที่ใช้งานได้')).toBeTruthy()
    await waitFor(() => expect(client.listAvailableSpaces).toHaveBeenCalledTimes(2))
  })
})
