import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import LoanKioskPage from '../pages/LoanKioskPage.jsx'

describe('T-05 borrow kiosk UI', () => {
  it('AC-LNS-01: ยืมสำเร็จเห็นวันกำหนดคืนและข้อความแจ้งเตือนล่วงหน้า', async () => {
    const client = {
      borrowBook: vi.fn().mockResolvedValue({
        allowed: true,
        status: 'approved',
        loan_id: 'loan-001',
        due_date: '2026-11-26',
        message: 'ยืมสำเร็จ',
        notifications: [{ channel: 'email', status: 'scheduled' }],
      }),
    }

    render(<LoanKioskPage client={client} />)

    fireEvent.change(screen.getByLabelText('รหัสสมาชิก'), { target: { value: 'STD-1001' } })
    fireEvent.change(screen.getByLabelText('บาร์โค้ด / QR Code หนังสือ'), { target: { value: 'BC-101' } })
    fireEvent.click(screen.getByRole('button', { name: 'ยืมหนังสือ' }))

    await waitFor(() => expect(client.borrowBook).toHaveBeenCalledWith({ memberId: 'STD-1001', barcode: 'BC-101', source: 'counter' }))
    expect((await screen.findAllByText('ยืมสำเร็จ')).length).toBeGreaterThan(0)
    expect(screen.getByText('กำหนดคืน: 26 พ.ย. 2569')).toBeTruthy()
    expect(screen.getByText('ระบบจะแจ้งเตือนล่วงหน้า 1–3 วันก่อนกำหนดคืน ผ่านระบบแจ้งเตือนและอีเมล')).toBeTruthy()
  })

  it('AC-LNS-02: เมื่อยืมครบโควตาเห็นข้อความปฏิเสธ', async () => {
    const client = {
      borrowBook: vi.fn().mockRejectedValue({
        status: 400,
        detail: 'ยืมครบจำนวนหนังสือที่สามารถยืมได้แล้ว',
      }),
    }

    render(<LoanKioskPage client={client} />)

    fireEvent.change(screen.getByLabelText('รหัสสมาชิก'), { target: { value: 'STD-1001' } })
    fireEvent.change(screen.getByLabelText('บาร์โค้ด / QR Code หนังสือ'), { target: { value: 'BC-102' } })
    fireEvent.click(screen.getByRole('button', { name: 'ยืมหนังสือ' }))

    expect((await screen.findAllByText('ไม่สามารถยืมได้')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('ยืมครบจำนวนหนังสือที่สามารถยืมได้แล้ว').length).toBeGreaterThan(0)
  })
})
