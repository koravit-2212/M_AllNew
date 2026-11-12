// T-08 (FR-EQP-03, FR-EQP-04, NFR-USB-01) ตรวจด้วย AC-EQP-02
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import StaffLoanApprovalPage from '../pages/StaffLoanApprovalPage.jsx'

const PENDING = {
  request_id: 'REQ-0001',
  status: 'pending',
  quantity: 1,
  student: { student_id: 'S1', name: 'นักศึกษาทดสอบ 1' },
  outstanding_items: [],
  equipment: { equipment_type_id: 'A', name: 'อุปกรณ์ทดสอบ', available_count: 3 },
}

describe('AC-EQP-02 เจ้าหน้าที่อนุมัติ ระบบบันทึกการยืมและลดจำนวนคงเหลือ', () => {
  it('AC-EQP-02 เห็นนักศึกษา อุปกรณ์ รายการค้างคืนไม่มี กดอนุมัติแล้วเห็นบันทึกการยืมแล้วและคงเหลือใหม่', async () => {
    // Given อุปกรณ์มีจำนวนเพียงพอและนักศึกษาไม่มีรายการค้างคืน
    const client = {
      listPendingLoanRequests: vi
        .fn()
        .mockResolvedValueOnce({ items: [PENDING] })
        .mockResolvedValue({ items: [] }),
      approveLoanRequest: vi.fn().mockResolvedValue({
        loan_id: 'LOAN-0001',
        request_id: 'REQ-0001',
        equipment_name: 'อุปกรณ์ทดสอบ',
        quantity: 1,
        available_count: 2,
      }),
    }
    render(<StaffLoanApprovalPage client={client} />)
    expect(screen.getByRole('heading', { name: 'อนุมัติคำขอยืมอุปกรณ์ (เจ้าหน้าที่)' })).toBeTruthy()

    // เจ้าหน้าที่เปิดคำขอและตรวจข้อมูลนักศึกษา (FR-EQP-03)
    fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ 1/ }))
    const card = within(screen.getByLabelText('ข้อมูลคำขอ'))
    expect(card.getByText('นักศึกษาทดสอบ 1 (S1)')).toBeTruthy()
    expect(card.getByText('อุปกรณ์ทดสอบ × 1')).toBeTruthy()
    expect(card.getByText('รายการค้างคืน')).toBeTruthy()
    expect(card.getByText('ไม่มี')).toBeTruthy()

    // When เจ้าหน้าที่อนุมัติการยืม
    fireEvent.click(screen.getByRole('button', { name: 'อนุมัติการยืม' }))

    // Then ระบบบันทึกการยืมและแสดงจำนวนคงเหลือที่ลดลง
    await waitFor(() => expect(client.approveLoanRequest).toHaveBeenCalledWith('REQ-0001'))
    expect(await screen.findByText('บันทึกการยืมแล้ว')).toBeTruthy()
    expect(screen.getByText('อุปกรณ์ทดสอบคงเหลือ 2')).toBeTruthy()
    expect(screen.queryByRole('button', { name: /นักศึกษาทดสอบ 1/ })).toBeNull()
  })
})
