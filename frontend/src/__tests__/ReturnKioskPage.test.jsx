import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import ReturnKioskPage from '../pages/ReturnKioskPage.jsx'

describe('T-07 return kiosk UI', () => {
  it('AC-LNS-03: คืนหนังสือเกินกำหนดแสดงป้ายคืนสำเร็จพร้อมจำนวนวันที่และค่าปรับ', async () => {
    const client = {
      returnBook: vi.fn().mockResolvedValue({
        status: 'returned',
        loan_id: 'loan-201',
        overdue_days: 4,
        penalty_amount: 12,
        message: 'คืนสำเร็จ เกินกำหนด 4 วัน ค่าปรับ 12 บาท',
      }),
    }

    render(<ReturnKioskPage client={client} />)

    fireEvent.change(screen.getByLabelText('รหัสสมาชิก'), { target: { value: 'STD-1001' } })
    fireEvent.change(screen.getByLabelText('บาร์โค้ด / QR Code หนังสือ'), { target: { value: 'BC-201' } })
    fireEvent.click(screen.getByRole('button', { name: 'คืนหนังสือ' }))

    await waitFor(() => expect(client.returnBook).toHaveBeenCalledWith({ memberId: 'STD-1001', barcode: 'BC-201' }))
    expect(await screen.findByText('คืนสำเร็จ')).toBeTruthy()
    expect(screen.getByText('เกินกำหนด 4 วัน')).toBeTruthy()
    expect(screen.getByText('ค่าปรับ 12 บาท')).toBeTruthy()
  })
})
